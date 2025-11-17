"""
크로스체인 확장 데모 - 설정 가능 버전
하드코딩된 값들을 파라미터로 변경
"""

import networkx as nx
import random
import json
from datetime import datetime, timedelta

class CrossChainDemo:
    """
    크로스체인 확장 시뮬레이션 (설정 가능)
    """
    
    def __init__(self, config=None):
        """
        Parameters:
        - config: 설정 딕셔너리
        """
        # ⚙️ 기본 설정 (하드코딩 제거!)
        default_config = {
            'chains': ['ethereum', 'polygon', 'bsc'],  # 🔧 하드코딩 1
            'tokens_per_chain': 20,                    # 🔧 하드코딩 2
            'wallets_per_token': 50,                   # 🔧 하드코딩 3
            'transaction_probability': 0.7,            # 🔧 하드코딩 4 (0.3에서 역전)
            'min_tx_value': 100,                       # 🔧 하드코딩 5
            'max_tx_value': 100000,                    # 🔧 하드코딩 6
            'high_risk_threshold': 70,                 # 🔧 하드코딩 7
            'bridge_sample_wallets': 100,              # 🔧 하드코딩 8
            'time_window_days': 30,                    # 🔧 하드코딩 9
            'suspicion_threshold': 60                  # 🔧 하드코딩 10
        }
        
        # 사용자 설정으로 덮어쓰기
        self.config = {**default_config, **(config or {})}
        
        self.chains = self.config['chains']
        self.unified_graph = nx.MultiDiGraph()
        self.bridge_info = self._load_bridges()
        
        print("⚙️  설정:")
        for key, value in self.config.items():
            print(f"   {key}: {value}")
        print()
        
    def _load_bridges(self):
        """브릿지 정보 로드"""
        try:
            with open('dataset/bridge_contracts.json', 'r') as f:
                return json.load(f)
        except:
            # 기본 브릿지 정보 (하드코딩 - 실제로는 JSON에서)
            print("⚠️  bridge_contracts.json 없음. 기본값 사용")
            return {
                "bridges": [
                    {
                        "name": "Hop Protocol",
                        "contracts": {
                            chain: f"0xHOP_{chain[:3].upper()}..." 
                            for chain in self.chains
                        }
                    },
                    {
                        "name": "Multichain",
                        "contracts": {
                            chain: f"0xMULTI_{chain[:3].upper()}..."
                            for chain in self.chains
                        }
                    }
                ]
            }
    
    def create_sample_network(self):
        """
        샘플 멀티체인 네트워크 생성
        """
        print("🔨 샘플 크로스체인 네트워크 생성 중...\n")
        
        tokens_per_chain = self.config['tokens_per_chain']
        wallets_per_token = self.config['wallets_per_token']
        
        for chain in self.chains:
            print(f"  {chain.upper()}: {tokens_per_chain}개 토큰, "
                  f"각 {wallets_per_token}개 지갑")
            
            for token_id in range(tokens_per_chain):
                # 토큰 노드
                token_node = f"{chain}:token_{token_id}"
                self.unified_graph.add_node(
                    token_node,
                    chain=chain,
                    type='token',
                    risk_score=random.uniform(0, 100)
                )
                
                # 지갑 노드들
                for wallet_id in range(wallets_per_token):
                    wallet_node = f"{chain}:wallet_{token_id}_{wallet_id}"
                    self.unified_graph.add_node(
                        wallet_node,
                        chain=chain,
                        type='wallet'
                    )
                    
                    # 거래 엣지 (확률 기반)
                    if random.random() < self.config['transaction_probability']:
                        self.unified_graph.add_edge(
                            wallet_node,
                            token_node,
                            type='transaction',
                            value=random.uniform(
                                self.config['min_tx_value'],
                                self.config['max_tx_value']
                            ),
                            timestamp=datetime.now() - timedelta(
                                days=random.randint(0, self.config['time_window_days'])
                            )
                        )
        
        print(f"\n✅ 기본 네트워크 생성 완료")
        print(f"   노드: {self.unified_graph.number_of_nodes():,}개")
        print(f"   엣지: {self.unified_graph.number_of_edges():,}개")
    
    def add_cross_chain_connections(self):
        """
        브릿지를 통한 크로스체인 연결 추가
        """
        print("\n🌉 크로스체인 연결 추가 중...")
        
        cross_chain_edges = 0
        
        # 각 브릿지에 대해
        for bridge in self.bridge_info['bridges']:
            bridge_name = bridge['name']
            
            # 브릿지 노드 생성
            bridge_nodes = {}
            for chain, contract in bridge['contracts'].items():
                if chain not in self.chains:
                    continue
                    
                node_id = f"{chain}:bridge_{bridge_name}"
                self.unified_graph.add_node(
                    node_id,
                    chain=chain,
                    type='bridge',
                    bridge_name=bridge_name
                )
                bridge_nodes[chain] = node_id
            
            # 브릿지 노드들 연결 (양방향)
            chains_list = list(bridge_nodes.keys())
            for i, chain1 in enumerate(chains_list):
                for chain2 in chains_list[i+1:]:
                    self.unified_graph.add_edge(
                        bridge_nodes[chain1],
                        bridge_nodes[chain2],
                        type='bridge_connection',
                        bridge_name=bridge_name
                    )
                    self.unified_graph.add_edge(
                        bridge_nodes[chain2],
                        bridge_nodes[chain1],
                        type='bridge_connection',
                        bridge_name=bridge_name
                    )
                    cross_chain_edges += 2
        
        # 일부 지갑들을 브릿지에 연결
        wallet_nodes = [n for n in self.unified_graph.nodes()
                       if self.unified_graph.nodes[n].get('type') == 'wallet']
        
        sample_size = min(self.config['bridge_sample_wallets'], len(wallet_nodes))
        sample_wallets = random.sample(wallet_nodes, sample_size)
        
        for wallet in sample_wallets:
            wallet_chain = self.unified_graph.nodes[wallet]['chain']
            
            # 해당 체인의 브릿지 찾기
            bridge_nodes = [n for n in self.unified_graph.nodes()
                           if self.unified_graph.nodes[n].get('type') == 'bridge'
                           and self.unified_graph.nodes[n].get('chain') == wallet_chain]
            
            if bridge_nodes:
                bridge = random.choice(bridge_nodes)
                self.unified_graph.add_edge(
                    wallet,
                    bridge,
                    type='bridge_transaction',
                    value=random.uniform(
                        self.config['min_tx_value'] * 10,  # 브릿지는 큰 금액
                        self.config['max_tx_value']
                    )
                )
                cross_chain_edges += 1
        
        print(f"✅ {cross_chain_edges}개의 크로스체인 엣지 추가")
        print(f"   총 노드: {self.unified_graph.number_of_nodes():,}개")
        print(f"   총 엣지: {self.unified_graph.number_of_edges():,}개")
    
    def find_suspicious_cross_chain_paths(self):
        """
        의심스러운 크로스체인 경로 탐지
        """
        print("\n🔍 의심스러운 크로스체인 경로 탐지...\n")
        
        suspicious_paths = []
        
        # 높은 리스크 토큰 찾기
        high_risk_tokens = [
            n for n in self.unified_graph.nodes()
            if self.unified_graph.nodes[n].get('type') == 'token'
            and self.unified_graph.nodes[n].get('risk_score', 0) > self.config['high_risk_threshold']
        ]
        
        print(f"   높은 리스크 토큰: {len(high_risk_tokens)}개 발견")
        
        for token in high_risk_tokens[:5]:  # 상위 5개만
            # 해당 토큰에서 브릿지로 가는 경로
            paths = self._trace_cross_chain_path(token, max_depth=4)
            
            for path in paths:
                if len(set([self.unified_graph.nodes[n]['chain'] 
                           for n in path])) >= 2:  # 2개 이상 체인
                    
                    suspicion_score = self._calculate_path_suspicion(path)
                    
                    if suspicion_score > self.config['suspicion_threshold']:
                        suspicious_paths.append({
                            'start': token,
                            'path': path,
                            'chains_involved': list(set([
                                self.unified_graph.nodes[n]['chain'] 
                                for n in path
                            ])),
                            'suspicion_score': suspicion_score
                        })
        
        # 의심도 순 정렬
        suspicious_paths.sort(key=lambda x: x['suspicion_score'], reverse=True)
        
        # 상위 10개 출력
        print("🚨 상위 의심 경로 10개:\n")
        
        for i, path_info in enumerate(suspicious_paths[:10], 1):
            print(f"[{i}] 의심도: {path_info['suspicion_score']:.0f}/100")
            print(f"    시작: {path_info['start']}")
            print(f"    거친 체인: {', '.join(path_info['chains_involved'])}")
            print(f"    경로 길이: {len(path_info['path'])}단계")
            print(f"    경로: {' → '.join([n[:25] for n in path_info['path'][:4]])}")
            print()
        
        if not suspicious_paths:
            print("   의심 경로 없음 (임계값을 낮춰보세요)")
        
        return suspicious_paths
    
    def _trace_cross_chain_path(self, start_node, max_depth=4):
        """경로 추적 (DFS)"""
        paths = []
        
        def dfs(node, path, depth):
            if depth >= max_depth:
                if len(path) > 1:
                    paths.append(path.copy())
                return
            
            for neighbor in self.unified_graph.neighbors(node):
                if neighbor not in path:
                    path.append(neighbor)
                    dfs(neighbor, path, depth + 1)
                    path.pop()
        
        dfs(start_node, [start_node], 0)
        return paths
    
    def _calculate_path_suspicion(self, path):
        """경로 의심도 계산"""
        score = 0
        
        # 1. 체인 개수 (30점)
        unique_chains = len(set([
            self.unified_graph.nodes[n]['chain'] for n in path
        ]))
        score += min(unique_chains * 15, 30)
        
        # 2. 경로 길이 (30점)
        score += min(len(path) * 7, 30)
        
        # 3. 브릿지 사용 (40점)
        bridge_count = sum(1 for n in path 
                          if self.unified_graph.nodes[n].get('type') == 'bridge')
        score += min(bridge_count * 20, 40)
        
        return min(score, 100)
    
    def generate_statistics(self):
        """통계 생성"""
        print("\n" + "=" * 70)
        print("📊 크로스체인 네트워크 통계")
        print("=" * 70 + "\n")
        
        # 체인별 통계
        for chain in self.chains:
            chain_nodes = [n for n in self.unified_graph.nodes()
                          if self.unified_graph.nodes[n].get('chain') == chain]
            
            tokens = sum(1 for n in chain_nodes 
                        if self.unified_graph.nodes[n].get('type') == 'token')
            wallets = sum(1 for n in chain_nodes
                         if self.unified_graph.nodes[n].get('type') == 'wallet')
            bridges = sum(1 for n in chain_nodes
                         if self.unified_graph.nodes[n].get('type') == 'bridge')
            
            print(f"{chain.upper()}:")
            print(f"  토큰: {tokens}개")
            print(f"  지갑: {wallets}개")
            print(f"  브릿지: {bridges}개")
            print()
        
        # 크로스체인 연결 통계
        cross_chain_edges = sum(
            1 for u, v in self.unified_graph.edges()
            if self.unified_graph.nodes[u]['chain'] != 
               self.unified_graph.nodes[v]['chain']
        )
        
        total_edges = self.unified_graph.number_of_edges()
        print(f"크로스체인 연결: {cross_chain_edges}개")
        if total_edges > 0:
            print(f"전체 연결 대비 비율: {cross_chain_edges/total_edges*100:.1f}%")


def run_demo(config=None):
    """
    데모 실행 함수
    
    Parameters:
    - config: 설정 딕셔너리
    """
    print("=" * 70)
    print("🌐 크로스체인 AML 시스템 - 설정 가능 버전")
    print("=" * 70)
    print()
    
    # 1. 초기화
    demo = CrossChainDemo(config)
    
    # 2. 샘플 네트워크 생성
    demo.create_sample_network()
    
    # 3. 크로스체인 연결 추가
    demo.add_cross_chain_connections()
    
    # 4. 통계
    demo.generate_statistics()
    
    # 5. 의심 경로 탐지
    suspicious = demo.find_suspicious_cross_chain_paths()
    
    print("\n" + "=" * 70)
    print("🔧 하드코딩 제거 완료!")
    print("=" * 70)
    print()
    print("설정 가능한 파라미터:")
    print("  - chains: 분석할 블록체인 목록")
    print("  - tokens_per_chain: 체인당 토큰 수")
    print("  - wallets_per_token: 토큰당 지갑 수")
    print("  - transaction_probability: 거래 발생 확률")
    print("  - min_tx_value, max_tx_value: 거래 금액 범위")
    print("  - high_risk_threshold: 고위험 임계값")
    print("  - suspicion_threshold: 의심 임계값")
    print()
    return demo, suspicious


if __name__ == "__main__":
    # ===== 시나리오 1: 기본 설정 =====
    print("\n" + "🎬 시나리오 1: 기본 설정\n" + "=" * 70 + "\n")
    demo1, suspicious1 = run_demo()
    
    # ===== 시나리오 2: 작은 네트워크 (빠른 테스트) =====
    print("\n\n" + "🎬 시나리오 2: 작은 네트워크 (빠른 테스트)\n" + "=" * 70 + "\n")
    small_config = {
        'tokens_per_chain': 5,
        'wallets_per_token': 10,
        'suspicion_threshold': 50  # 더 낮은 임계값
    }
    demo2, suspicious2 = run_demo(small_config)
    
    # ===== 시나리오 3: 고위험 환경 =====
    print("\n\n" + "🎬 시나리오 3: 고위험 환경\n" + "=" * 70 + "\n")
    high_risk_config = {
        'high_risk_threshold': 50,  # 더 많은 고위험 토큰
        'transaction_probability': 0.9,  # 거래 많음
        'min_tx_value': 10000,  # 큰 금액만
        'max_tx_value': 1000000,
        'suspicion_threshold': 40  # 낮은 임계값
    }
    demo3, suspicious3 = run_demo(high_risk_config)
    
    # ===== 결과 비교 =====
    print("\n\n" + "=" * 70)
    print("📊 시나리오별 결과 비교")
    print("=" * 70)
    print()
    print(f"시나리오 1 (기본):      {len(suspicious1)}건의 의심 경로")
    print(f"시나리오 2 (작은):      {len(suspicious2)}건의 의심 경로")
    print(f"시나리오 3 (고위험):    {len(suspicious3)}건의 의심 경로")
    print()
    print("✅ 모든 시나리오 완료!")

