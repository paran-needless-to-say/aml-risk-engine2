"""
룰 평가기

TRACE-X 룰북 기반 룰 평가
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional
from core.rules.loader import RuleLoader
from core.data.lists import ListLoader
from core.aggregation.window import WindowEvaluator
from core.aggregation.bucket import BucketEvaluator
from core.aggregation.ppr_connector import PPRConnector
from core.aggregation.mpocryptml_patterns import MPOCryptoMLPatternDetector
from core.aggregation.stats import StatisticsCalculator
from core.aggregation.topology import TopologyEvaluator


class RuleEvaluator:
    """룰 평가기"""
    
    def __init__(self, rules_path: str = "rules/tracex_rules.yaml", window_evaluator: Optional[WindowEvaluator] = None, bucket_evaluator: Optional[BucketEvaluator] = None):
        """
        Args:
            rules_path: 룰북 YAML 파일 경로
            window_evaluator: 윈도우 평가기 (None이면 새로 생성)
            bucket_evaluator: 버킷 평가기 (None이면 새로 생성)
        """
        self.rule_loader = RuleLoader(rules_path)
        self.list_loader = ListLoader()
        self.ruleset = self.rule_loader.load()
        self.window_evaluator = window_evaluator or WindowEvaluator()
        self.bucket_evaluator = bucket_evaluator or BucketEvaluator()
        self.ppr_connector = PPRConnector()
        self.pattern_detector = None  # 필요 시 생성
        self.stats_calculator = StatisticsCalculator()
        self.topology_evaluator = TopologyEvaluator()
    
    def evaluate_single_transaction(
        self,
        tx_data: Dict[str, Any],
        include_topology: bool = False
    ) -> List[Dict[str, Any]]:
        """
        단일 트랜잭션에 대한 룰 평가
        
        Args:
            tx_data: 트랜잭션 데이터 (from, to, usd_value, timestamp 등)
            include_topology: 그래프 구조 분석 룰 포함 여부 (기본값: False, 성능 최적화)
        
        Returns:
            발동된 룰 목록 [{"rule_id": "...", "score": 30, ...}, ...]
        """
        fired_rules = []
        rules = self.rule_loader.get_rules()
        lists = self.list_loader.get_all_lists()
        
        # 트랜잭션 히스토리에 추가 (윈도우 평가를 위해)
        target_address = tx_data.get("to") or tx_data.get("target_address")
        if target_address:
            self.window_evaluator.history.add_transaction(target_address, tx_data)
        
        for rule in rules:
            rule_id = rule.get("id")
            if not rule_id:
                continue
            
            # 미지원 룰 타입 건너뛰기
            # state는 아직 미구현
            # bucket은 이제 지원됨
            # prerequisites는 B-103에서 구현됨
            # topology는 B-201, B-202에서 구현됨 (3홉 데이터 필요)
            # E-103은 커스터마이징 항목으로 남김 (백엔드 데이터 필요)
            if "state" in rule:
                continue  # state 룰은 아직 미구현
            
            # E-103은 커스터마이징 항목 (백엔드에서 counterparty.risk_score 제공 시 작동)
            if rule_id == "E-103":
                # tag 기반 조건이 없으면 건너뜀 (백엔드 데이터 필요)
                conditions = rule.get("conditions", {})
                if not conditions:
                    continue
            
            # E-102: PPR로 간접 제재 노출 탐지
            if rule_id == "E-102":
                if self._evaluate_e102_with_ppr(tx_data, rule, lists):
                    # 조건 확인
                    if not self._check_conditions(tx_data, rule, lists):
                        continue
                    # 예외 확인
                    if self._check_exceptions(tx_data, rule, lists):
                        continue
                    # 룰 발동
                    score = rule.get("score", 30)
                    fired_rules.append({
                        "rule_id": rule_id,
                        "score": float(score),
                        "axis": rule.get("axis", "E"),
                        "name": rule.get("name", rule_id),
                        "severity": rule.get("severity", "HIGH"),
                        "source": "PPR"  # PPR 기반 탐지
                    })
                continue  # E-102는 여기서 처리 완료
            
            # B-103: Prerequisites 및 통계 계산 필요
            if rule_id == "B-103":
                if self._evaluate_b103_with_stats(tx_data, rule, lists):
                    # 조건 확인 (interarrival_std는 이미 계산됨)
                    if not self._check_conditions(tx_data, rule, lists):
                        continue
                    # 예외 확인
                    if self._check_exceptions(tx_data, rule, lists):
                        continue
                    # 룰 발동
                    score = rule.get("score", 10)
                    fired_rules.append({
                        "rule_id": rule_id,
                        "score": float(score),
                        "axis": rule.get("axis", "B"),
                        "name": rule.get("name", rule_id),
                        "severity": rule.get("severity", "LOW")
                    })
                continue  # B-103는 여기서 처리 완료
            
            # B-201, B-202: Topology 기반 룰 (3홉 데이터 필요, 성능 최적화를 위해 옵션)
            if rule_id == "B-201":
                if not include_topology:
                    continue  # 기본 스코어링에서는 제외
                if self._evaluate_topology_rule(tx_data, rule, "layering_chain"):
                    # 조건 확인
                    if not self._check_conditions(tx_data, rule, lists):
                        continue
                    # 예외 확인
                    if self._check_exceptions(tx_data, rule, lists):
                        continue
                    # 룰 발동
                    score = rule.get("score", 25)
                    fired_rules.append({
                        "rule_id": rule_id,
                        "score": float(score),
                        "axis": rule.get("axis", "B"),
                        "name": rule.get("name", rule_id),
                        "severity": rule.get("severity", "HIGH")
                    })
                continue
            
            if rule_id == "B-202":
                if not include_topology:
                    continue  # 기본 스코어링에서는 제외
                if self._evaluate_topology_rule(tx_data, rule, "cycle"):
                    # 조건 확인
                    if not self._check_conditions(tx_data, rule, lists):
                        continue
                    # 예외 확인
                    if self._check_exceptions(tx_data, rule, lists):
                        continue
                    # 룰 발동
                    score = rule.get("score", 30)
                    fired_rules.append({
                        "rule_id": rule_id,
                        "score": float(score),
                        "axis": rule.get("axis", "B"),
                        "name": rule.get("name", rule_id),
                        "severity": rule.get("severity", "HIGH")
                    })
                continue
            
            # 버킷 기반 룰인지 확인 (bucket 또는 buckets)
            has_bucket = "bucket" in rule or "buckets" in rule
            
            # B-501: buckets 기반 동적 점수 룰 (특별 처리)
            if rule_id == "B-501":
                buckets_spec = rule.get("buckets")
                if buckets_spec:
                    # 동적 점수 계산
                    field = buckets_spec.get("field", "usd_value")
                    ranges = buckets_spec.get("ranges", [])
                    value = float(tx_data.get(field, 0))
                    
                    # 범위에 맞는 점수 찾기
                    dynamic_score = 0
                    for range_spec in ranges:
                        min_val = range_spec.get("min", 0)
                        max_val = range_spec.get("max", float('inf'))
                        if min_val <= value < max_val:
                            dynamic_score = range_spec.get("score", 0)
                            break
                    
                    # 점수가 0보다 크면 룰 발동
                    if dynamic_score > 0:
                        fired_rules.append({
                            "rule_id": rule_id,
                            "score": float(dynamic_score),
                            "axis": rule.get("axis", "B"),
                            "name": rule.get("name", rule_id),
                            "severity": rule.get("severity", "MEDIUM")
                        })
                continue  # B-501은 여기서 처리 완료
            
            # 윈도우 기반 룰인지 확인
            has_window = "window" in rule or ("aggregations" in rule and not has_bucket)
            
            if has_bucket:
                # 버킷 기반 룰 평가 (B-203, B-204)
                if not self.bucket_evaluator.evaluate_bucket_rule(tx_data, rule):
                    continue
            elif has_window:
                # 윈도우 기반 룰 평가
                if not self.window_evaluator.evaluate_window_rule(tx_data, rule):
                    continue
            else:
                # 단일 트랜잭션 룰 평가
                # 룰 매칭 확인
                if not self._match_rule(tx_data, rule, lists):
                    continue
                
                # 조건 확인
                if not self._check_conditions(tx_data, rule, lists):
                    continue
            
            # 예외 확인
            if self._check_exceptions(tx_data, rule, lists):
                continue
            
            # 룰 발동
            score = rule.get("score", 0)
            # score가 문자열("dynamic" 등)이면 0으로 처리
            if isinstance(score, str):
                try:
                    score = float(score)
                except (ValueError, TypeError):
                    score = 0
            
            fired_rules.append({
                "rule_id": rule_id,
                "score": float(score),
                "axis": rule.get("axis", "B"),
                "name": rule.get("name", rule_id),
                "severity": rule.get("severity", "MEDIUM")
            })
        
        return fired_rules
    
    def _match_rule(
        self,
        tx_data: Dict[str, Any],
        rule: Dict[str, Any],
        lists: Dict[str, set]
    ) -> bool:
        """룰 매칭 확인"""
        match_clause = rule.get("match")
        if not match_clause:
            return True  # match가 없으면 항상 매칭
        
        return self._eval_match_clause(tx_data, match_clause, lists)
    
    def _check_conditions(
        self,
        tx_data: Dict[str, Any],
        rule: Dict[str, Any],
        lists: Dict[str, set]
    ) -> bool:
        """조건 확인"""
        conditions = rule.get("conditions")
        if not conditions:
            return True
        
        return self._eval_conditions(tx_data, conditions, lists)
    
    def _check_exceptions(
        self,
        tx_data: Dict[str, Any],
        rule: Dict[str, Any],
        lists: Dict[str, set]
    ) -> bool:
        """예외 확인 (예외가 있으면 룰 발동 안 함)"""
        exceptions = rule.get("exceptions")
        if not exceptions:
            return False
        
        return self._eval_conditions(tx_data, exceptions, lists)
    
    def _eval_match_clause(
        self,
        tx_data: Dict[str, Any],
        match_clause: Dict[str, Any],
        lists: Dict[str, set]
    ) -> bool:
        """매칭 절 평가"""
        if "any" in match_clause:
            return any(
                self._eval_single_match(tx_data, item, lists)
                for item in match_clause["any"]
            )
        elif "all" in match_clause:
            return all(
                self._eval_single_match(tx_data, item, lists)
                for item in match_clause["all"]
            )
        else:
            return self._eval_single_match(tx_data, match_clause, lists)
    
    def _eval_single_match(
        self,
        tx_data: Dict[str, Any],
        match_item: Dict[str, Any],
        lists: Dict[str, set]
    ) -> bool:
        """단일 매칭 항목 평가"""
        if "in_list" in match_item:
            spec = match_item["in_list"]
            field = spec.get("field")
            list_name = spec.get("list")
            value = tx_data.get(field, "").lower() if field else ""
            target_list = lists.get(list_name, set())
            
            # 리스트에 직접 있는지 확인
            if value in target_list:
                return True
            
            # 백엔드에서 제공하는 플래그 활용
            # SDN_LIST: is_sanctioned 플래그 확인
            if list_name == "SDN_LIST" and tx_data.get("is_sanctioned", False):
                return True
            
            # MIXER_LIST: is_mixer 플래그 확인
            if list_name == "MIXER_LIST" and tx_data.get("is_mixer", False):
                return True
            
            return False
        
        return False
    
    def _eval_conditions(
        self,
        tx_data: Dict[str, Any],
        conditions: Dict[str, Any],
        lists: Dict[str, set]
    ) -> bool:
        """조건 평가"""
        if "all" in conditions:
            return all(
                self._eval_single_condition(tx_data, item, lists)
                for item in conditions["all"]
            )
        elif "any" in conditions:
            return any(
                self._eval_single_condition(tx_data, item, lists)
                for item in conditions["any"]
            )
        else:
            return self._eval_single_condition(tx_data, conditions, lists)
    
    def _evaluate_e102_with_ppr(
        self,
        tx_data: Dict[str, Any],
        rule: Dict[str, Any],
        lists: Dict[str, set]
    ) -> bool:
        """
        E-102 룰 평가: PPR을 사용한 간접 제재 노출 탐지
        
        Args:
            tx_data: 트랜잭션 데이터
            rule: E-102 룰 정의
            lists: 리스트 데이터 (SDN, MIXER 등)
        
        Returns:
            룰 발동 여부
        """
        target_address = tx_data.get("to") or tx_data.get("target_address", "")
        if not target_address:
            return False
        
        # 트랜잭션 히스토리에서 그래프 구축
        # window_evaluator의 history를 활용
        history = self.window_evaluator.history
        
        # 타겟 주소의 트랜잭션 히스토리 가져오기 (최근 365일)
        address_history = history._history.get(target_address.lower(), [])
        
        if len(address_history) < 2:
            # 트랜잭션이 너무 적으면 PPR 계산 불가
            return False
        
        # 그래프 구축
        if self.pattern_detector is None:
            self.pattern_detector = MPOCryptoMLPatternDetector()
        else:
            self.pattern_detector._build_graph()  # 그래프 초기화
        
        # 히스토리 트랜잭션을 그래프에 추가
        for tx in address_history:
            self.pattern_detector.add_transaction(tx)
        
        # 현재 트랜잭션도 추가
        self.pattern_detector.add_transaction(tx_data)
        
        if not self.pattern_detector.graph or target_address.lower() not in self.pattern_detector.graph:
            return False
        
        # SDN 및 믹서 주소 리스트
        sdn_addresses = lists.get("SDN_LIST", set())
        mixer_addresses = lists.get("MIXER_LIST", set())
        
        # PPR 연결성 계산
        ppr_result = self.ppr_connector.calculate_connection_risk(
            target_address,
            self.pattern_detector.graph,
            sdn_addresses,
            mixer_addresses
        )
        
        # 임계값 체크 (PPR >= 0.05면 간접 연결성 높음)
        ppr_threshold = 0.05
        
        return ppr_result["total_ppr"] >= ppr_threshold
    
    def _evaluate_b103_with_stats(
        self,
        tx_data: Dict[str, Any],
        rule: Dict[str, Any],
        lists: Dict[str, set]
    ) -> bool:
        """
        B-103 룰 평가: Prerequisites 및 통계 계산
        
        Args:
            tx_data: 트랜잭션 데이터
            rule: B-103 룰 정의
            lists: 리스트 데이터
        
        Returns:
            룰 발동 여부
        """
        # Prerequisites 체크
        prerequisites = rule.get("prerequisites", [])
        if prerequisites:
            for prereq in prerequisites:
                if "min_edges" in prereq:
                    min_edges = prereq["min_edges"]
                    # 트랜잭션 히스토리에서 거래 수 확인
                    target_address = tx_data.get("to") or tx_data.get("target_address", "")
                    if target_address:
                        history = self.window_evaluator.history
                        address_history = history._history.get(target_address.lower(), [])
                        
                        # 현재 트랜잭션 포함
                        all_transactions = address_history + [tx_data]
                        
                        if not self.stats_calculator.check_prerequisites(all_transactions, min_edges):
                            return False  # Prerequisites 불만족
        
        # 통계 계산
        target_address = tx_data.get("to") or tx_data.get("target_address", "")
        if not target_address:
            return False
        
        history = self.window_evaluator.history
        address_history = history._history.get(target_address.lower(), [])
        
        # 현재 트랜잭션 포함
        all_transactions = address_history + [tx_data]
        
        # 거래 간격 표준편차 계산
        interarrival_std = self.stats_calculator.calculate_interarrival_std(all_transactions)
        
        if interarrival_std is None:
            return False
        
        # tx_data에 계산된 값을 추가 (조건 평가를 위해)
        tx_data["interarrival_std"] = interarrival_std
        
        return True
    
    def _evaluate_topology_rule(
        self,
        tx_data: Dict[str, Any],
        rule: Dict[str, Any],
        rule_type: str  # "layering_chain" or "cycle"
    ) -> bool:
        """
        Topology 기반 룰 평가 (B-201, B-202)
        
        Args:
            tx_data: 현재 트랜잭션 데이터
            rule: 룰 정의
            rule_type: 룰 타입 ("layering_chain" or "cycle")
        
        Returns:
            룰 발동 여부
        """
        target_address = tx_data.get("to") or tx_data.get("target_address", "")
        if not target_address:
            return False
        
        # 트랜잭션 히스토리에서 그래프 구축
        # window_evaluator의 history를 활용
        history = self.window_evaluator.history
        
        # 타겟 주소의 트랜잭션 히스토리 가져오기
        address_history = history._history.get(target_address.lower(), [])
        
        # 현재 트랜잭션 포함
        all_transactions = address_history + [tx_data]
        
        # Topology 룰 설정
        topology_spec = rule.get("topology", {})
        
        if rule_type == "layering_chain":
            return self.topology_evaluator.evaluate_layering_chain(
                target_address,
                all_transactions,
                topology_spec
            )
        elif rule_type == "cycle":
            return self.topology_evaluator.evaluate_cycle(
                target_address,
                all_transactions,
                topology_spec
            )
        
        return False
    
    def _eval_single_condition(
        self,
        tx_data: Dict[str, Any],
        condition: Dict[str, Any],
        lists: Dict[str, set]
    ) -> bool:
        """단일 조건 평가"""
        # gte, lte, gt, lt, eq 등
        for op in ["gte", "lte", "gt", "lt", "eq"]:
            if op in condition:
                spec = condition[op]
                field = spec.get("field")
                value = spec.get("value")
                tx_value = tx_data.get(field, 0)
                
                if op == "gte":
                    return float(tx_value) >= float(value)
                elif op == "lte":
                    return float(tx_value) <= float(value)
                elif op == "gt":
                    return float(tx_value) > float(value)
                elif op == "lt":
                    return float(tx_value) < float(value)
                elif op == "eq":
                    return tx_value == value
        
        return False

