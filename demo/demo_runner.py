"""
시연용 데이터로 주소 분석 실행

사용자가 주소 하나를 입력하면 그 주소에 대한 리스크 스코어링만 수행
API 구조와 동일한 형식으로 출력

사용법:
    프로젝트 루트에서 실행:
    python demo/demo_runner.py [주소]
    
    예시:
    python demo/demo_runner.py 0xhigh_risk_mixer_sanctioned
    python demo/demo_runner.py 0xlow_risk_normal
"""
import json
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.scoring.address_analyzer import AddressAnalyzer


def load_transactions(address: str) -> list:
    """주소의 거래 히스토리 로드"""
    demo_dir = Path(__file__).parent
    tx_file = demo_dir / "transactions" / f"{address}_txs.json"
    if not tx_file.exists():
        return []
    
    with open(tx_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_available_addresses() -> dict:
    """사용 가능한 주소 목록 반환"""
    demo_dir = Path(__file__).parent
    addresses_file = demo_dir / "addresses.json"
    with open(addresses_file, "r", encoding="utf-8") as f:
        return json.load(f)


def format_api_response(result) -> dict:
    """API 응답 형식으로 변환"""
    # fired_rules를 API 형식으로 변환 (rule_id, score만)
    fired_rules_api = []
    for rule in result.fired_rules:
        if isinstance(rule, dict):
            fired_rules_api.append({
                "rule_id": rule.get("rule_id", ""),
                "score": int(rule.get("score", 0))
            })
        else:
            # 객체인 경우
            fired_rules_api.append({
                "rule_id": getattr(rule, "rule_id", ""),
                "score": int(getattr(rule, "score", 0))
            })
    
    return {
        "target_address": result.address,
        "risk_score": int(result.risk_score),
        "risk_level": result.risk_level,
        "risk_tags": result.risk_tags,
        "fired_rules": fired_rules_api,
        "explanation": result.explanation,
        "completed_at": result.completed_at
    }


def print_api_response(response: dict):
    """API 응답 형식으로 출력"""
    print("=" * 70)
    print("📊 주소 리스크 분석 결과")
    print("=" * 70)
    print()
    print(f"주소: {response['target_address']}")
    print(f"리스크 스코어: {response['risk_score']}")
    print(f"리스크 레벨: {response['risk_level']}")
    print()
    print(f"발동된 룰: {len(response['fired_rules'])}개")
    for rule in response['fired_rules']:
        print(f"  - {rule['rule_id']}: {rule['score']}점")
    print()
    print(f"리스크 태그: {', '.join(response['risk_tags']) if response['risk_tags'] else '없음'}")
    print()
    print(f"설명: {response['explanation']}")
    print()
    print(f"스코어링 완료 시각: {response['completed_at']}")
    print()
    print("=" * 70)


def analyze_single_address(address: str, chain: str = "ethereum") -> dict:
    """단일 주소 분석 (API와 동일한 방식)"""
    transactions = load_transactions(address)
    if not transactions:
        return None
    
    # API와 동일한 방식으로 분석
    analyzer = AddressAnalyzer()
    result = analyzer.analyze_address(address, chain, transactions)
    
    # API 응답 형식으로 변환
    return format_api_response(result)


def run_demo():
    """시연 실행"""
    # 명령줄 인자로 주소 받기
    if len(sys.argv) > 1:
        address = sys.argv[1]
        chain = sys.argv[2] if len(sys.argv) > 2 else "ethereum"
        
        print("=" * 70)
        print("🎬 주소 리스크 분석 (API 구조 동일)")
        print("=" * 70)
        print()
        
        # 주소 분석
        result = analyze_single_address(address, chain)
        
        if result:
            print_api_response(result)
            print("✅ 분석 완료")
        else:
            print(f"❌ 오류: 주소 '{address}'의 거래 데이터를 찾을 수 없습니다.")
            print()
            print_available_addresses()
    else:
        # 주소가 없으면 사용 가능한 주소 목록 표시
        print("=" * 70)
        print("🎬 주소 리스크 분석 데모")
        print("=" * 70)
        print()
        print("사용법: python demo/demo_runner.py [주소]")
        print()
        print_available_addresses()


def print_available_addresses():
    """사용 가능한 주소 목록 출력"""
    addresses_data = get_available_addresses()
    
    print("📋 사용 가능한 데모 주소:")
    print()
    
    print("🔴 High Risk:")
    for addr_info in addresses_data["high_risk"]:
        print(f"  - {addr_info['address']}: {addr_info['description']}")
    
    print()
    print("🟡 Medium Risk:")
    for addr_info in addresses_data["medium_risk"]:
        print(f"  - {addr_info['address']}: {addr_info['description']}")
    
    print()
    print("🟢 Low Risk:")
    for addr_info in addresses_data["low_risk"]:
        print(f"  - {addr_info['address']}: {addr_info['description']}")
    
    print()
    print("예시:")
    print("  python demo/demo_runner.py 0xhigh_risk_mixer_sanctioned")
    print("  python demo/demo_runner.py 0xlow_risk_normal")


if __name__ == "__main__":
    run_demo()
