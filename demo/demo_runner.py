"""
시연용 데이터로 주소 분석 실행

다양한 리스크 레벨의 주소들을 분석하여 결과 확인

사용법:
    프로젝트 루트에서 실행:
    python demo/demo_runner.py
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


def run_demo():
    """시연 실행"""
    print("=" * 70)
    print("🎬 시연용 데이터 분석")
    print("=" * 70)
    print()
    
    # 주소 목록 로드
    demo_dir = Path(__file__).parent
    addresses_file = demo_dir / "addresses.json"
    with open(addresses_file, "r", encoding="utf-8") as f:
        addresses_data = json.load(f)
    
    analyzer = AddressAnalyzer()
    
    # High Risk 주소 분석
    print("🔴 High Risk 주소 분석")
    print("-" * 70)
    for addr_info in addresses_data["high_risk"]:
        address = addr_info["address"]
        chain = addr_info["chain"]
        description = addr_info["description"]
        expected_score = addr_info["expected_score"]
        expected_level = addr_info["expected_level"]
        
        transactions = load_transactions(address)
        if not transactions:
            print(f"  ⚠️  {address}: 거래 데이터 없음")
            continue
        
        result = analyzer.analyze_address(address, chain, transactions)
        
        # 기존 JSON 포맷으로 출력 (시연용 - 실제 API 응답과 동일)
        print(f"\n  주소: {address}")
        print(f"  설명: {description} (시연용)")
        print(f"  리스크 스코어: {int(result.risk_score)}")
        print(f"  리스크 레벨: {result.risk_level}")
        print(f"  발동된 룰: {len(result.fired_rules)}개")
        for rule in result.fired_rules:
            print(f"    - {rule['rule_id']}: {rule['score']}점")
        print(f"  리스크 태그: {', '.join(result.risk_tags) if result.risk_tags else '없음'}")
        print(f"  설명: {result.explanation}")
    
    print()
    print("🟡 Medium Risk 주소 분석")
    print("-" * 70)
    for addr_info in addresses_data["medium_risk"]:
        address = addr_info["address"]
        chain = addr_info["chain"]
        description = addr_info["description"]
        expected_score = addr_info["expected_score"]
        expected_level = addr_info["expected_level"]
        
        transactions = load_transactions(address)
        if not transactions:
            print(f"  ⚠️  {address}: 거래 데이터 없음")
            continue
        
        result = analyzer.analyze_address(address, chain, transactions)
        
        # 기존 JSON 포맷으로 출력 (시연용 - 실제 API 응답과 동일)
        print(f"\n  주소: {address}")
        print(f"  설명: {description} (시연용)")
        print(f"  리스크 스코어: {int(result.risk_score)}")
        print(f"  리스크 레벨: {result.risk_level}")
        print(f"  발동된 룰: {len(result.fired_rules)}개")
        for rule in result.fired_rules:
            print(f"    - {rule['rule_id']}: {rule['score']}점")
        print(f"  리스크 태그: {', '.join(result.risk_tags) if result.risk_tags else '없음'}")
        print(f"  설명: {result.explanation}")
    
    print()
    print("🟢 Low Risk 주소 분석")
    print("-" * 70)
    for addr_info in addresses_data["low_risk"]:
        address = addr_info["address"]
        chain = addr_info["chain"]
        description = addr_info["description"]
        expected_score = addr_info["expected_score"]
        expected_level = addr_info["expected_level"]
        
        transactions = load_transactions(address)
        if not transactions:
            print(f"  ⚠️  {address}: 거래 데이터 없음")
            continue
        
        result = analyzer.analyze_address(address, chain, transactions)
        
        print(f"\n  주소: {address}")
        print(f"  설명: {description}")
        print(f"  리스크 스코어: {result.risk_score:.1f} (예상: {expected_score})")
        print(f"  리스크 레벨: {result.risk_level} (예상: {expected_level})")
        print(f"  총 거래 수: {result.analysis_summary['total_transactions']}")
        print(f"  총 거래액: ${result.analysis_summary['total_volume_usd']:,.2f}")
        print(f"  발동된 룰: {len(result.fired_rules)}개")
        if result.fired_rules:
            for rule in result.fired_rules:
                print(f"    - {rule['rule_id']}: {rule['name']} (점수: {rule['score']}, 발동: {rule['count']}회)")
        print(f"  리스크 태그: {', '.join(result.risk_tags) if result.risk_tags else '없음'}")
    
    print()
    print("=" * 70)
    print("✅ 시연 완료")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()

