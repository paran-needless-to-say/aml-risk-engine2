"""
트랜잭션 스코어링 엔진

백엔드에서 받은 트랜잭션 정보를 기반으로 AML 스코어링 수행
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from core.rules.evaluator import RuleEvaluator
from core.data.lists import ListLoader


@dataclass
class TransactionInput:
    """백엔드에서 받는 트랜잭션 정보"""
    tx_hash: str
    chain: str
    timestamp: str  # ISO8601 UTC
    block_height: int
    target_address: str
    counterparty_address: str
    entity_type: str  # mixer | bridge | cex | dex | defi | unknown
    is_sanctioned: bool
    is_known_scam: bool
    is_mixer: bool
    is_bridge: bool
    amount_usd: float
    asset_contract: str


@dataclass
class FiredRule:
    """발동된 룰 정보"""
    rule_id: str
    score: float


@dataclass
class ScoringResult:
    """최종 스코어링 결과"""
    target_address: str
    risk_score: float  # 0~100
    risk_level: str  # low | medium | high | critical
    risk_tags: List[str]
    fired_rules: List[FiredRule]
    explanation: str


class TransactionScorer:
    """트랜잭션 스코어링 엔진"""
    
    def __init__(self, rules_path: str = "rules/tracex_rules.yaml"):
        """
        Args:
            rules_path: 룰북 YAML 파일 경로
        """
        self.rule_evaluator = RuleEvaluator(rules_path)
        self.list_loader = ListLoader()
    
    def score_transaction(self, tx_input: TransactionInput) -> ScoringResult:
        """
        트랜잭션 스코어링 수행
        
        Args:
            tx_input: 백엔드에서 받은 트랜잭션 정보
        
        Returns:
            스코어링 결과
        """
        # 1. 백엔드 정보를 룰 평가용 데이터로 변환
        tx_data = self._convert_to_rule_data(tx_input)
        
        # 2. 룰 평가 (TRACE-X 룰북 기반)
        rule_results = self.rule_evaluator.evaluate_single_transaction(tx_data)
        
        # 3. 점수 계산
        risk_score = self._calculate_risk_score(rule_results)
        
        # 4. Risk Level 결정
        risk_level = self._determine_risk_level(risk_score)
        
        # 5. Risk Tags 생성
        risk_tags = self._generate_risk_tags(rule_results, tx_input)
        
        # 6. Fired Rules 목록 생성
        fired_rules = [
            FiredRule(rule_id=r["rule_id"], score=r["score"])
            for r in rule_results
        ]
        
        # 7. Explanation 생성
        explanation = self._generate_explanation(tx_input, rule_results, risk_level)
        
        return ScoringResult(
            target_address=tx_input.target_address,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_tags=risk_tags,
            fired_rules=fired_rules,
            explanation=explanation
        )
    
    def _convert_to_rule_data(self, tx: TransactionInput) -> Dict[str, Any]:
        """백엔드 JSON을 룰 평가용 데이터로 변환"""
        # 리스트 로드
        sdn_list = self.list_loader.get_sdn_list()
        mixer_list = self.list_loader.get_mixer_list()
        
        return {
            "from": tx.counterparty_address,
            "to": tx.target_address,
            "tx_hash": tx.tx_hash,
            "timestamp": tx.timestamp,
            "usd_value": tx.amount_usd,
            "chain": tx.chain,
            "block_height": tx.block_height,
            # 백엔드에서 제공하는 라벨 정보 활용
            "is_sanctioned": tx.is_sanctioned,
            "is_known_scam": tx.is_known_scam,
            "is_mixer": tx.is_mixer,
            "is_bridge": tx.is_bridge,
            "entity_type": tx.entity_type,
            "asset_contract": tx.asset_contract,
        }
    
    def _calculate_risk_score(self, rule_results: List[Dict[str, Any]]) -> float:
        """룰 결과를 기반으로 리스크 점수 계산"""
        total_score = sum(r.get("score", 0) for r in rule_results)
        # 0~100 범위로 정규화 (최대 점수는 룰북에 따라 조정)
        return min(100.0, total_score)
    
    def _determine_risk_level(self, score: float) -> str:
        """점수 기반 리스크 레벨 결정"""
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 30:
            return "medium"
        else:
            return "low"
    
    def _generate_risk_tags(
        self,
        rule_results: List[Dict[str, Any]],
        tx: TransactionInput
    ) -> List[str]:
        """Risk Tags 생성"""
        tags = []
        
        # 룰 결과에서 태그 추출
        for result in rule_results:
            rule_id = result.get("rule_id", "")
            if "MIXER" in rule_id:
                tags.append("mixer_inflow")
            elif "SANCTION" in rule_id:
                tags.append("sanction_exposure")
            elif "SCAM" in rule_id:
                tags.append("scam_exposure")
            elif "AMOUNT" in rule_id:
                tags.append("high_value_transfer")
            elif "BRIDGE" in rule_id:
                tags.append("bridge_large_transfer")
            elif "CEX" in rule_id:
                tags.append("cex_inflow")
        
        # 중복 제거
        return list(set(tags))
    
    def _generate_explanation(
        self,
        tx: TransactionInput,
        rule_results: List[Dict[str, Any]],
        risk_level: str
    ) -> str:
        """설명 텍스트 생성"""
        parts = []
        
        if tx.is_mixer:
            parts.append(f"1-hop mixer에서 {tx.amount_usd:,.0f}USD 유입")
        
        if tx.is_sanctioned:
            parts.append("제재 대상과 거래")
        
        if tx.is_known_scam:
            parts.append("알려진 사기 주소와 거래")
        
        if tx.amount_usd >= 1000:
            parts.append(f"고액 거래 ({tx.amount_usd:,.0f}USD)")
        
        if tx.is_bridge and tx.amount_usd >= 5000:
            parts.append("대량 브릿지 거래")
        
        if not parts:
            parts.append("일반 거래")
        
        explanation = ", ".join(parts)
        explanation += f"로 인해 {risk_level}로 분류됨."
        
        return explanation

