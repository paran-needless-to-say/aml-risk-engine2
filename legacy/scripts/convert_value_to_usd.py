#!/usr/bin/env python3
"""
거래 CSV의 value를 usd_value로 변환하는 스크립트
백엔드 API (CoinMarketCap)를 활용하여 토큰 가격 조회
"""
import os
import sys
import json
import requests
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# 백엔드 API 설정
CMC_API_KEY = os.getenv("CMC_PRO_API_KEY")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")  # 백엔드 API URL

# 기본 decimals (대부분의 토큰은 18)
DEFAULT_DECIMALS = 18

# 알려진 토큰의 decimals (예외 케이스)
KNOWN_DECIMALS = {
    # USDC, USDT는 6 decimals
    "ethereum:0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": 6,  # USDC (Ethereum)
    "ethereum:0xdac17f958d2ee523a2206206994597c13d831ec7": 6,  # USDT (Ethereum)
    "polygon:0x2791bca1f2de4661ed88a30c99a7a9449aa84174": 6,   # USDC (Polygon)
    "bsc:0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d": 18,      # USDC (BSC) - 18 decimals
    "bsc:0x55d398326f99059ff775485246999027b3197955": 18,      # USDT (BSC) - 18 decimals
}


def load_token_metadata() -> Dict[str, Dict[str, str]]:
    """토큰 메타데이터 로드 (Contract → Symbol 매핑)"""
    # 1. web_demo/mock_token_metadata.json에서 로드 시도
    metadata_path = Path("web_demo/mock_token_metadata.json")
    if metadata_path.exists():
        with metadata_path.open() as f:
            return json.load(f)
    
    # 2. 없으면 scripts/build_mock_token_metadata.py의 MANUAL_LABELS 사용
    return {
        "ethereum:0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": {"symbol": "USDC"},
        "ethereum:0xdac17f958d2ee523a2206206994597c13d831ec7": {"symbol": "USDT"},
        "ethereum:0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": {"symbol": "WBTC"},
        "ethereum:0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": {"symbol": "WETH"},
        "polygon:0x2791bca1f2de4661ed88a30c99a7a9449aa84174": {"symbol": "USDC"},
        "polygon:0x7ceb23fd6bc0add59e62ac25578270cff1b9f619": {"symbol": "WETH"},
        "polygon:0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270": {"symbol": "MATIC"},
        "bsc:0x55d398326f99059ff775485246999027b3197955": {"symbol": "USDT"},
        "bsc:0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d": {"symbol": "USDC"},
    }


# 가격 캐시 (같은 컨트랙트는 재요청 안 함)
_price_cache = {}
_last_request_time = 0
MIN_REQUEST_INTERVAL = 5.0  # 초 (Rate limit 방지, 무료 플랜 대응)

def get_token_price_by_contract_address(chain: str, contract: str) -> Optional[float]:
    """
    Contract 주소로 직접 토큰 가격 조회
    CoinGecko API 사용 (무료, Contract 주소 직접 지원)
    Rate limit 방지를 위한 캐싱 및 딜레이 포함
    """
    global _price_cache, _last_request_time
    
    # 캐시 확인
    cache_key = f"{chain}:{contract.lower()}"
    if cache_key in _price_cache:
        return _price_cache[cache_key]
    
    try:
        # Rate limit 방지: 요청 간 최소 간격 유지
        import time
        current_time = time.time()
        time_since_last = current_time - _last_request_time
        if time_since_last < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - time_since_last)
        
        # CoinGecko는 체인별로 다른 엔드포인트 사용
        chain_map = {
            "ethereum": "ethereum",
            "polygon": "polygon-pos",
            "bsc": "binance-smart-chain"
        }
        
        gecko_chain = chain_map.get(chain.lower())
        if not gecko_chain:
            return None
        
        # CoinGecko API: Contract 주소로 직접 조회
        url = f"https://api.coingecko.com/api/v3/simple/token_price/{gecko_chain}"
        params = {
            "contract_addresses": contract.lower(),
            "vs_currencies": "usd"
        }
        
        response = requests.get(url, params=params, timeout=10)
        _last_request_time = time.time()
        
        if response.status_code == 429:
            # Rate limit 에러 - 더 긴 대기 후 재시도 (최대 1회)
            print(f"⚠️  CoinGecko Rate Limit (429). 10초 대기 후 재시도...")
            time.sleep(10)
            response = requests.get(url, params=params, timeout=10)
            _last_request_time = time.time()
            
            if response.status_code == 429:
                print(f"   ❌ 재시도 후에도 Rate Limit. 컨트랙트: {contract[:20]}...")
                # 캐시에 None 저장하여 재요청 방지
                _price_cache[cache_key] = None
                return None
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        contract_lower = contract.lower()
        if contract_lower in data:
            price = data[contract_lower].get("usd")
            if price:
                price_float = float(price)
                # 캐시에 저장
                _price_cache[cache_key] = price_float
                return price_float
        
        # 가격이 없어도 캐시에 None 저장 (재요청 방지)
        _price_cache[cache_key] = None
        return None
        
    except Exception as e:
        # CoinGecko 실패 시 조용히 넘어감
        return None


def get_token_price_from_cmc_by_symbol(symbol: str) -> Optional[float]:
    """
    CoinMarketCap API를 통해 심볼로 토큰 가격 조회
    참고: https://github.com/paran-needless-to-say/backend/blob/main/api/utils/token/services.py
    """
    if not CMC_API_KEY:
        return None
    
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": CMC_API_KEY
        }
        params = {
            "symbol": symbol.upper(),
            "convert": "USD"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        try:
            price = data["data"][symbol.upper()]["quote"]["USD"]["price"]
            return float(price)
        except (KeyError, TypeError):
            return None
            
    except Exception:
        return None


def get_token_price_from_cmc_by_contract(chain: str, contract: str) -> Optional[float]:
    """
    CoinMarketCap API: Contract 주소로 토큰 ID 찾기 → 가격 조회
    """
    if not CMC_API_KEY:
        return None
    
    try:
        # 1단계: Contract 주소로 토큰 정보 찾기 (map 엔드포인트)
        # 참고: CoinMarketCap의 map 엔드포인트는 Contract 주소를 직접 지원하지 않을 수 있음
        # 대신 CoinGecko를 우선 사용하고, 실패 시 심볼 기반 조회
        
        # 일단 None 반환 (CoinGecko가 우선)
        return None
        
    except Exception:
        return None


def get_token_price(chain: str, contract: str, symbol: Optional[str] = None) -> Optional[float]:
    """
    Contract 주소로 토큰 가격 조회 (여러 방법 시도)
    
    우선순위:
    1. CoinGecko API (Contract 주소 직접 지원, 무료)
    2. CoinMarketCap API (심볼 기반, 유료 API 키 필요)
    """
    # 방법 1: CoinGecko로 Contract 주소 직접 조회 (추천)
    price = get_token_price_by_contract_address(chain, contract)
    if price is not None:
        return price
    
    # 방법 2: 심볼이 있으면 CoinMarketCap 사용
    if symbol:
        price = get_token_price_from_cmc_by_symbol(symbol)
        if price is not None:
            return price
    
    return None


def get_token_decimals(chain: str, contract: str) -> int:
    """토큰의 decimals 가져오기"""
    key = f"{chain}:{contract.lower()}"
    return KNOWN_DECIMALS.get(key, DEFAULT_DECIMALS)


def get_token_symbol(chain: str, contract: str, metadata: Dict) -> Optional[str]:
    """Contract 주소에서 토큰 심볼 가져오기"""
    key = f"{chain}:{contract.lower()}"
    token_info = metadata.get(key, {})
    return token_info.get("symbol")


def convert_value_to_usd(
    value: int,
    chain: str,
    contract: str,
    decimals: Optional[int] = None,
    symbol: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Optional[float]:
    """
    value를 USD로 변환
    
    Args:
        value: 토큰의 최소 단위 (wei)
        chain: 체인 이름 (ethereum, polygon, bsc)
        contract: 컨트랙트 주소
        decimals: 토큰 decimals (없으면 자동 조회)
        symbol: 토큰 심볼 (없으면 메타데이터에서 조회)
        metadata: 토큰 메타데이터
    
    Returns:
        USD 가치 (변환 실패 시 None)
    """
    # 1. decimals 가져오기
    if decimals is None:
        decimals = get_token_decimals(chain, contract)
    
    # 2. 토큰 단위로 변환
    token_amount = value / (10 ** decimals)
    
    # 3. 심볼 가져오기 (선택적, CoinGecko는 심볼 불필요)
    if symbol is None:
        if metadata is None:
            metadata = load_token_metadata()
        symbol = get_token_symbol(chain, contract, metadata)
    
    # 4. 가격 가져오기 (Contract 주소로 직접 조회)
    price = get_token_price(chain, contract, symbol)
    if price is None:
        if symbol:
            print(f"⚠️  가격을 가져올 수 없음: {chain}:{contract} (심볼: {symbol})")
        else:
            print(f"⚠️  가격을 가져올 수 없음: {chain}:{contract}")
        return None
    
    # 5. USD 변환
    usd_value = token_amount * price
    
    return usd_value


def convert_transaction_csv(
    csv_path: Path,
    chain: str,
    contract: str,
    metadata: Optional[Dict] = None
) -> pd.DataFrame:
    """거래 CSV에 usd_value 컬럼 추가"""
    print(f"📄 처리 중: {csv_path.name}")
    
    df = pd.read_csv(csv_path)
    
    # 이미 usd_value가 있으면 스킵
    if "usd_value" in df.columns:
        print(f"  ✓ usd_value 컬럼이 이미 존재합니다.")
        return df
    
    # 메타데이터 로드
    if metadata is None:
        metadata = load_token_metadata()
    
    # decimals 가져오기
    decimals = get_token_decimals(chain, contract)
    
    # 심볼 가져오기 (선택적, CoinGecko는 심볼 불필요)
    symbol = get_token_symbol(chain, contract, metadata)
    
    # 가격 조회 (Contract 주소로 직접 조회)
    price = get_token_price(chain, contract, symbol)
    if price is None:
        if symbol:
            print(f"  ⚠️  가격을 가져올 수 없어 변환을 건너뜁니다. (Contract: {contract[:10]}..., 심볼: {symbol})")
        else:
            print(f"  ⚠️  가격을 가져올 수 없어 변환을 건너뜁니다. (Contract: {contract[:10]}...)")
        df["usd_value"] = None
        return df
    
    # 가격 정보 출력
    if symbol:
        print(f"  ℹ️  {symbol} 가격: ${price:.6f} (Contract: {contract[:10]}...)")
    else:
        print(f"  ℹ️  토큰 가격: ${price:.6f} (Contract: {contract[:10]}...)")
    
    # usd_value 계산
    usd_values = []
    for idx, row in df.iterrows():
        try:
            value = int(row["value"])
            token_amount = value / (10 ** decimals)
            usd_value = token_amount * price
            usd_values.append(usd_value)
        except (ValueError, TypeError) as e:
            print(f"  ⚠️  행 {idx} 변환 실패: {e}")
            usd_values.append(None)
    
    df["usd_value"] = usd_values
    
    # 통계 출력
    valid_values = [v for v in usd_values if v is not None]
    if valid_values:
        print(f"  ✓ 변환 완료: {len(valid_values)}개 거래")
        print(f"    - 최소: ${min(valid_values):.2f}")
        print(f"    - 최대: ${max(valid_values):.2f}")
        print(f"    - 평균: ${sum(valid_values)/len(valid_values):.2f}")
    
    return df


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="거래 CSV의 value를 usd_value로 변환")
    parser.add_argument("--chain", required=True, choices=["ethereum", "polygon", "bsc"], help="체인 이름")
    parser.add_argument("--contract", help="특정 컨트랙트만 처리 (없으면 전체)")
    parser.add_argument("--input-dir", default="data/transactions", help="입력 디렉토리")
    parser.add_argument("--output-dir", default="data/transactions_with_usd", help="출력 디렉토리")
    parser.add_argument("--in-place", action="store_true", help="원본 파일에 직접 추가")
    
    args = parser.parse_args()
    
    # 환경변수 확인
    if not CMC_API_KEY:
        print("❌ 오류: CMC_PRO_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   export CMC_PRO_API_KEY='your-api-key'")
        sys.exit(1)
    
    # 디렉토리 설정
    input_dir = Path(args.input_dir) / args.chain
    if args.in_place:
        output_dir = input_dir
    else:
        output_dir = Path(args.output_dir) / args.chain
        output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        print(f"❌ 오류: 입력 디렉토리가 존재하지 않습니다: {input_dir}")
        sys.exit(1)
    
    # 메타데이터 로드
    print("📚 토큰 메타데이터 로드 중...")
    metadata = load_token_metadata()
    print(f"  ✓ {len(metadata)}개 토큰 정보 로드됨")
    
    # CSV 파일 처리
    if args.contract:
        csv_files = [input_dir / f"{args.contract}.csv"]
    else:
        csv_files = list(input_dir.glob("*.csv"))
    
    print(f"\n📊 {len(csv_files)}개 파일 처리 시작...\n")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for csv_file in csv_files:
        try:
            contract = csv_file.stem
            df = convert_transaction_csv(csv_file, args.chain, contract, metadata)
            
            # 저장
            if args.in_place:
                output_path = csv_file
            else:
                output_path = output_dir / csv_file.name
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)
            
            success_count += 1
            print()
            
        except Exception as e:
            print(f"  ❌ 오류 발생: {e}\n")
            error_count += 1
    
    # 결과 요약
    print("=" * 70)
    print(f"✅ 완료: {success_count}개 성공, {skip_count}개 스킵, {error_count}개 실패")
    if not args.in_place:
        print(f"📁 출력 디렉토리: {output_dir}")


if __name__ == "__main__":
    main()

