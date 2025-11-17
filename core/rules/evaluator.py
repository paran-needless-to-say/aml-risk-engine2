"""
룰 평가기

TRACE-X 룰북 기반 룰 평가
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional
from core.rules.loader import RuleLoader
from core.data.lists import ListLoader
from core.aggregation.window import WindowEvaluator


class RuleEvaluator:
    """룰 평가기"""
    
    def __init__(self, rules_path: str = "rules/tracex_rules.yaml", window_evaluator: Optional[WindowEvaluator] = None):
        """
        Args:
            rules_path: 룰북 YAML 파일 경로
            window_evaluator: 윈도우 평가기 (None이면 새로 생성)
        """
        self.rule_loader = RuleLoader(rules_path)
        self.list_loader = ListLoader()
        self.ruleset = self.rule_loader.load()
        self.window_evaluator = window_evaluator or WindowEvaluator()
    
    def evaluate_single_transaction(self, tx_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        단일 트랜잭션에 대한 룰 평가
        
        Args:
            tx_data: 트랜잭션 데이터 (from, to, usd_value, timestamp 등)
        
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
            # topology, buckets, state, prerequisites 등은 아직 미구현
            if any(key in rule for key in ["topology", "buckets", "state", "prerequisites"]):
                continue  # 이런 룰들은 건너뛰기
            
            # 윈도우 기반 룰인지 확인
            has_window = "window" in rule or "aggregations" in rule
            
            if has_window:
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

