"""
크로스체인 자금 흐름 추적 시스템
Multi-chain AML을 위한 확장 모듈
"""

import pandas as pd
import networkx as nx
from typing import Dict, List, Tuple
import json

class CrossChainTracker:
    """
    여러 블록체인을 아우르는 자금 흐름 추적
    """
    
    def __init__(self, chains: List[str]):
        """
        Parameters:
        - chains: ['ethereum', 'polygon', 'bsc']
        """
        self.chains = chains
        self.unified_graph = nx.MultiDiGraph()  # 통합 그래프
        self.wallet_mapping = {}  # 지갑 → 사용자 매핑
        self.bridge_transactions = []  # 브릿지 거래 기록
        
    def load_chain_data(self, chain: str, labels_path: str, transactions_path: str):
        """
        각 체인의 데이터 로드
        """
        labels = pd.read_csv(labels_path).query(f'Chain == "{chain}"')
        
        # 체인별 거래 데이터 통합
        chain_graph = nx.DiGraph()
        
        for contract in labels['Contract'].values:
            try:
                tx = pd.read_csv(f'{transactions_path}/{chain}/{contract}.csv')
                
                for _, row in tx.iterrows():
                    # 멀티체인 노드 ID 생성 (체인 접두사 추가)
                    from_node = f"{chain}:{row['from']}"
                    to_node = f"{chain}:{row['to']}"
                    
                    self.unified_graph.add_edge(
                        from_node, 
                        to_node,
                        chain=chain,
                        value=row['value'],
                        timestamp=row['timestamp'],
                        tx_hash=row['hash']
                    )
            except Exception as e:
                print(f"Error loading {contract}: {e}")
                
        return chain_graph
    
    def detect_bridge_transactions(self, bridge_contracts: Dict[str, List[str]]):
        """
        브릿지 컨트랙트를 통한 크로스체인 거래 탐지
        
        Parameters:
        - bridge_contracts: {
            'ethereum': ['0xA0b86991...', '0x1a2b3c...'],  # Hop, Multichain 등
            'polygon': ['0xB1c97a12...'],
            'bsc': ['0xC2d86a23...']
          }
        """
        
        cross_chain_flows = []
        
        for chain, contracts in bridge_contracts.items():
            for contract in contracts:
                node_id = f"{chain}:{contract}"
                
                if node_id in self.unified_graph:
                    # 브릿지로 들어오는 거래
                    in_edges = list(self.unified_graph.in_edges(node_id, data=True))
                    
                    # 브릿지에서 나가는 거래
                    out_edges = list(self.unified_graph.out_edges(node_id, data=True))
                    
                    # 시간대별 매칭 (보통 5-30분 이내)
                    for in_edge in in_edges:
                        source, _, in_data = in_edge
                        in_time = pd.to_datetime(in_data['timestamp'], unit='s')
                        
                        for out_edge in out_edges:
                            _, target, out_data = out_edge
                            out_time = pd.to_datetime(out_data['timestamp'], unit='s')
                            
                            time_diff = (out_time - in_time).total_seconds()
                            
                            # 5분~30분 사이에 나간 거래는 크로스체인 의심
                            if 300 < time_diff < 1800:
                                target_chain = target.split(':')[0]
                                
                                if target_chain != chain:  # 다른 체인으로
                                    cross_chain_flows.append({
                                        'from_chain': chain,
                                        'to_chain': target_chain,
                                        'source_wallet': source,
                                        'target_wallet': target,
                                        'bridge': node_id,
                                        'value': in_data['value'],
                                        'time_diff_seconds': time_diff,
                                        'in_tx': in_data['tx_hash'],
                                        'out_tx': out_data['tx_hash']
                                    })
        
        self.bridge_transactions = cross_chain_flows
        return cross_chain_flows
    
    def cluster_wallets_by_behavior(self):
        """
        행동 패턴으로 지갑 클러스터링 (같은 사용자 추정)
        
        방법:
        1. 같은 시간대에 활동
        2. 비슷한 거래 금액
        3. 공통 상대방
        4. 브릿지를 통해 연결
        """
        
        wallet_features = {}
        
        for node in self.unified_graph.nodes():
            chain, address = node.split(':', 1)
            
            # 각 지갑의 행동 특징 추출
            edges = list(self.unified_graph.edges(node, data=True))
            
            if not edges:
                continue
                
            timestamps = [e[2]['timestamp'] for e in edges]
            values = [float(e[2]['value']) if isinstance(e[2]['value'], (int, float)) 
                     else 0 for e in edges]
            
            wallet_features[node] = {
                'chain': chain,
                'tx_count': len(edges),
                'avg_value': sum(values) / len(values) if values else 0,
                'active_hours': self._extract_active_hours(timestamps),
                'counterparties': self._get_counterparties(node)
            }
        
        # 유사도 기반 클러스터링
        clusters = self._cluster_by_similarity(wallet_features)
        
        return clusters
    
    def _extract_active_hours(self, timestamps):
        """거래 시간대 패턴 추출"""
        if not timestamps:
            return set()
        
        hours = set()
        for ts in timestamps:
            try:
                dt = pd.to_datetime(ts, unit='s')
                hours.add(dt.hour)
            except:
                continue
        return hours
    
    def _get_counterparties(self, node):
        """거래 상대방 추출"""
        counterparties = set()
        
        # 받은 거래
        for _, target, _ in self.unified_graph.in_edges(node, data=True):
            counterparties.add(target)
        
        # 보낸 거래
        for source, _, _ in self.unified_graph.out_edges(node, data=True):
            counterparties.add(source)
            
        return counterparties
    
    def _cluster_by_similarity(self, wallet_features):
        """유사도 기반 클러스터링"""
        clusters = []
        processed = set()
        
        wallets = list(wallet_features.keys())
        
        for i, wallet1 in enumerate(wallets):
            if wallet1 in processed:
                continue
                
            cluster = [wallet1]
            processed.add(wallet1)
            
            for wallet2 in wallets[i+1:]:
                if wallet2 in processed:
                    continue
                
                # 유사도 계산
                similarity = self._calculate_similarity(
                    wallet_features[wallet1],
                    wallet_features[wallet2]
                )
                
                # 70% 이상 유사하면 같은 사용자로 추정
                if similarity > 0.7:
                    cluster.append(wallet2)
                    processed.add(wallet2)
            
            if len(cluster) > 1:  # 2개 이상 지갑 연결된 경우만
                clusters.append(cluster)
        
        return clusters
    
    def _calculate_similarity(self, f1, f2):
        """두 지갑의 유사도 계산"""
        score = 0.0
        
        # 1. 활동 시간대 유사도
        if f1['active_hours'] and f2['active_hours']:
            hour_overlap = len(f1['active_hours'] & f2['active_hours'])
            hour_union = len(f1['active_hours'] | f2['active_hours'])
            score += 0.3 * (hour_overlap / hour_union if hour_union > 0 else 0)
        
        # 2. 평균 거래 금액 유사도
        if f1['avg_value'] > 0 and f2['avg_value'] > 0:
            value_ratio = min(f1['avg_value'], f2['avg_value']) / max(f1['avg_value'], f2['avg_value'])
            score += 0.3 * value_ratio
        
        # 3. 공통 거래 상대방
        if f1['counterparties'] and f2['counterparties']:
            common_parties = len(f1['counterparties'] & f2['counterparties'])
            total_parties = len(f1['counterparties'] | f2['counterparties'])
            score += 0.4 * (common_parties / total_parties if total_parties > 0 else 0)
        
        return score
    
    def trace_cross_chain_flow(self, start_wallet: str, max_hops: int = 5):
        """
        특정 지갑에서 시작한 크로스체인 자금 흐름 추적
        
        Returns:
        - 자금 경로 및 의심도
        """
        
        paths = []
        
        def dfs(current, path, visited, chain_count):
            if len(path) > max_hops:
                return
            
            # 여러 체인을 거쳤으면 의심스러움
            if len(chain_count) >= 3:
                paths.append({
                    'path': path.copy(),
                    'chains_used': list(chain_count.keys()),
                    'suspicion_score': len(chain_count) * 20,
                    'reason': 'Multiple chain hopping detected'
                })
            
            if current not in self.unified_graph:
                return
                
            for _, next_node, data in self.unified_graph.out_edges(current, data=True):
                if next_node not in visited:
                    new_chain_count = chain_count.copy()
                    chain = data['chain']
                    new_chain_count[chain] = new_chain_count.get(chain, 0) + 1
                    
                    path.append({
                        'node': next_node,
                        'chain': chain,
                        'value': data['value'],
                        'tx_hash': data['tx_hash']
                    })
                    visited.add(next_node)
                    
                    dfs(next_node, path, visited, new_chain_count)
                    
                    path.pop()
                    visited.remove(next_node)
        
        start_chain = start_wallet.split(':')[0]
        dfs(start_wallet, [{'node': start_wallet, 'chain': start_chain}], 
            {start_wallet}, {start_chain: 1})
        
        return sorted(paths, key=lambda x: x['suspicion_score'], reverse=True)


# 사용 예시
if __name__ == "__main__":
    
    print("=" * 60)
    print("크로스체인 AML 추적 시스템")
    print("=" * 60)
    
    # 1. 초기화
    tracker = CrossChainTracker(['ethereum', 'polygon', 'bsc'])
    
    print("\n📊 시스템 구성:")
    print("  • Ethereum, Polygon, BSC 통합 분석")
    print("  • 브릿지 거래 자동 탐지")
    print("  • 행동 패턴 기반 지갑 클러스터링")
    
    # 2. 브릿지 컨트랙트 정의 (실제 주소 예시)
    bridge_contracts = {
        'ethereum': [
            '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  # USDC (자주 브릿지로 사용)
            '0x3666f603Cc164936C1b87e207F36BEBa4AC5f18a',  # Hop Protocol
        ],
        'polygon': [
            '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',  # USDC on Polygon
        ],
        'bsc': [
            '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',  # USDC on BSC
        ]
    }
    
    print("\n🌉 등록된 브릿지 컨트랙트:")
    for chain, contracts in bridge_contracts.items():
        print(f"  {chain}: {len(contracts)}개")
    
    # 3. 예시 결과 시뮬레이션
    print("\n" + "=" * 60)
    print("예시: 의심스러운 크로스체인 거래 탐지 결과")
    print("=" * 60)
    
    suspicious_example = {
        'wallet_id': 'USER_12345',
        'wallets': [
            'ethereum:0xABC123...',
            'polygon:0xDEF456...',
            'bsc:0xGHI789...'
        ],
        'cross_chain_flow': [
            {
                'step': 1,
                'from': 'ethereum:0xABC123...',
                'to': 'ethereum:0x3666f603... (Hop Bridge)',
                'value': '50,000 USDC',
                'timestamp': '2024-10-11 09:15:23'
            },
            {
                'step': 2,
                'from': 'ethereum:Hop Bridge',
                'to': 'polygon:0xDEF456...',
                'value': '49,800 USDC',
                'timestamp': '2024-10-11 09:22:17',
                'time_taken': '6분 54초'
            },
            {
                'step': 3,
                'from': 'polygon:0xDEF456...',
                'to': 'polygon:0x2791Bca... (Bridge)',
                'value': '49,800 USDC',
                'timestamp': '2024-10-11 09:35:41'
            },
            {
                'step': 4,
                'from': 'polygon:Bridge',
                'to': 'bsc:0xGHI789...',
                'value': '49,600 USDC',
                'timestamp': '2024-10-11 09:48:09',
                'time_taken': '12분 28초'
            }
        ],
        'risk_analysis': {
            'risk_score': 87,
            'risk_level': 'CRITICAL',
            'flags': [
                '❌ 3개 체인을 연속으로 거침 (Chain Hopping)',
                '❌ 1시간 이내 급속 이동',
                '❌ 대량 자금 ($50,000)',
                '❌ 브릿지를 통한 의도적 추적 회피 의심',
                '⚠️  각 체인별 지갑이 동일 시간대 활동',
                '⚠️  거래 패턴 유사도: 92%'
            ],
            'scenario': 'S7_CROSS_CHAIN_LAYERING',
            'description': '크로스체인 레이어링 - 여러 체인을 거쳐 자금 출처 은폐 시도'
        }
    }
    
    print(f"\n🔍 의심 사용자: {suspicious_example['wallet_id']}")
    print(f"📊 리스크 점수: {suspicious_example['risk_analysis']['risk_score']}/100")
    print(f"⚠️  리스크 레벨: {suspicious_example['risk_analysis']['risk_level']}")
    
    print(f"\n💼 연결된 지갑 ({len(suspicious_example['wallets'])}개):")
    for wallet in suspicious_example['wallets']:
        print(f"  • {wallet}")
    
    print(f"\n🔄 자금 흐름 경로:")
    for step in suspicious_example['cross_chain_flow']:
        print(f"\n  [{step['step']}단계]")
        print(f"    From: {step['from']}")
        print(f"    To:   {step['to']}")
        print(f"    금액: {step['value']}")
        print(f"    시각: {step['timestamp']}")
        if 'time_taken' in step:
            print(f"    소요: {step['time_taken']}")
    
    print(f"\n⚠️  탐지된 의심 신호:")
    for flag in suspicious_example['risk_analysis']['flags']:
        print(f"  {flag}")
    
    print(f"\n📋 시나리오: {suspicious_example['risk_analysis']['scenario']}")
    print(f"📝 설명: {suspicious_example['risk_analysis']['description']}")
    
    print("\n" + "=" * 60)
    print("권장 조치:")
    print("=" * 60)
    print("  1. 🚨 즉시 해당 지갑들 모니터링 강화")
    print("  2. 📊 최근 30일 거래 이력 전수 조사")
    print("  3. 📄 SAR (Suspicious Activity Report) 제출 검토")
    print("  4. 🔒 필요시 거래 일시 제한 조치")
    print("  5. 🔍 연관된 다른 지갑 추가 조사")

