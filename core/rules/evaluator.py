"""
룰 평가기

TRACE-X 룰북 기반 룰 평가
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional
from core.rules.loader import RuleLoader
from core.data.lists import ListLoader


class RuleEvaluator:
    """룰 평가기"""
    
    def __init__(self, rules_path: str = "rules/tracex_rules.yaml"):
        """
        Args:
            rules_path: 룰북 YAML 파일 경로
        """
        self.rule_loader = RuleLoader(rules_path)
        self.list_loader = ListLoader()
        self.ruleset = self.rule_loader.load()
    
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
        
        for rule in rules:
            rule_id = rule.get("id")
            if not rule_id:
                continue
            
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
            fired_rules.append({
                "rule_id": rule_id,
                "score": score,
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
            return value in target_list
        
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

