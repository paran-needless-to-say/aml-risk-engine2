"""
시간/금액 패턴 분석 모듈 (NTS, NWS)

MPOCryptoML 논문의 시간 및 금액 패턴 분석
NTS: Node Temporal Score (노드 시간 특성)
NWS: Node Weight Score (노드 가중치 특성)
"""

from typing import Dict, List, Optional, Any
from collections import defaultdict
from datetime import datetime
import statistics
import networkx as nx


class TemporalPatternAnalyzer:
    """
    시간/금액 패턴 분석기
    
    노드의 시간적 특성(NTS)과 가중치 특성(NWS)을 분석
    """
    
    def calculate_nts(
        self,
        address: str,
        graph: nx.DiGraph,
        transactions: List[Dict[str, Any]]
    ) -> float:
        """
        Node Temporal Score (NTS) 계산
        
        노드의 시간적 특성을 분석:
        - 거래 간격의 규칙성
        - 시간대 분포
        - 거래 빈도
        
        Args:
            address: 분석 대상 주소
            graph: 거래 그래프
            transactions: 주소 관련 트랜잭션 리스트
        
        Returns:
            NTS 점수 (0~1, 높을수록 비정상적)
        """
        if not transactions:
            return 0.0
        
        address = address.lower()
        
        # 타임스탬프 추출 및 정렬
        timestamps = []
        for tx in transactions:
            ts = self._get_timestamp_int(tx)
            if ts:
                timestamps.append(ts)
        
        if len(timestamps) < 2:
            return 0.0
        
        timestamps.sort()
        
        # 거래 간격 계산
        intervals = []
        for i in range(1, len(timestamps)):
            interval = timestamps[i] - timestamps[i-1]
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        # 간격의 표준편차 (불규칙성 측정)
        try:
            interval_std = statistics.stdev(intervals) if len(intervals) > 1 else 0
            interval_mean = statistics.mean(intervals) if intervals else 0
            
            # 변동계수 (CV = std/mean)
            cv = interval_std / interval_mean if interval_mean > 0 else 0
            
            # NTS: 변동계수가 높을수록 비정상적 (0~1로 정규화)
            nts = min(1.0, cv / 2.0)  # CV 2.0 이상이면 1.0
        except:
            nts = 0.0
        
        return nts
    
    def calculate_nws(
        self,
        address: str,
        graph: nx.DiGraph,
        transactions: List[Dict[str, Any]]
    ) -> float:
        """
        Node Weight Score (NWS) 계산
        
        노드의 가중치(금액) 특성을 분석:
        - 거래 금액 분포
        - 평균/중앙값 비율
        - 이상치 존재 여부
        
        Args:
            address: 분석 대상 주소
            graph: 거래 그래프
            transactions: 주소 관련 트랜잭션 리스트
        
        Returns:
            NWS 점수 (0~1, 높을수록 비정상적)
        """
        if not transactions:
            return 0.0
        
        # 거래 금액 추출
        amounts = []
        for tx in transactions:
            amount = float(tx.get("usd_value", tx.get("amount_usd", 0)))
            if amount > 0:
                amounts.append(amount)
        
        if not amounts:
            return 0.0
        
        try:
            # 평균과 중앙값
            mean_amount = statistics.mean(amounts)
            median_amount = statistics.median(amounts)
            
            # 평균/중앙값 비율 (비대칭성 측정)
            if median_amount > 0:
                ratio = mean_amount / median_amount
            else:
                ratio = 0
            
            # 표준편차
            std_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            # 변동계수
            cv = std_amount / mean_amount if mean_amount > 0 else 0
            
            # NWS: 비대칭성과 변동성이 높을수록 비정상적
            # ratio가 2 이상이면 비대칭적 (큰 거래가 많음)
            # CV가 1 이상이면 변동성이 높음
            nws_asymmetry = min(1.0, (ratio - 1.0) / 2.0) if ratio > 1 else 0
            nws_variability = min(1.0, cv / 2.0)
            
            # 두 점수의 평균
            nws = (nws_asymmetry + nws_variability) / 2.0
        except:
            nws = 0.0
        
        return nws
    
    def _get_timestamp_int(self, tx: Dict[str, Any]) -> Optional[int]:
        """타임스탬프를 정수로 변환"""
        timestamp = tx.get("timestamp", 0)
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                return int(dt.timestamp())
            except:
                return None
        return int(timestamp) if timestamp else None
    
    def analyze_temporal_patterns(
        self,
        address: str,
        graph: nx.DiGraph,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        시간/금액 패턴 종합 분석
        
        Args:
            address: 분석 대상 주소
            graph: 거래 그래프
            transactions: 주소 관련 트랜잭션 리스트
        
        Returns:
            {
                "nts": float,  # Node Temporal Score
                "nws": float,  # Node Weight Score
                "combined_score": float,  # 종합 점수
                "risk_level": str  # low | medium | high
            }
        """
        nts = self.calculate_nts(address, graph, transactions)
        nws = self.calculate_nws(address, graph, transactions)
        
        # 종합 점수 (가중 평균)
        combined_score = (nts * 0.5 + nws * 0.5)
        
        # 리스크 레벨 결정
        if combined_score >= 0.7:
            risk_level = "high"
        elif combined_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "nts": nts,
            "nws": nws,
            "combined_score": combined_score,
            "risk_level": risk_level
        }

