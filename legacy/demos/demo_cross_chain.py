"""
크로스체인 확장 데모
실제 데이터 없이도 개념을 보여주는 시뮬레이션
"""

import networkx as nx
import random
import json
from datetime import datetime, timedelta

class CrossChainDemo:
    """
    크로스체인 확장 시뮬레이션
    """
    
    def __init__(self):
        self.chains = ['ethereum', 'polygon', 'bsc']
        self.unified_graph = nx.MultiDiGraph()
        self.bridge_info = self._load_bridges()
        
    def _load_bridges(self):
        """브릿지 정보 로드"""
        try:
            with open('dataset/bridge_contracts.json', 'r') as f:
                return json.load(f)
        except:
            # 기본 브릿지 정보
            return {
                "bridges": [
                    {
                        "name": "Hop Protocol",
                        "contracts": {
                            "ethereum": "0x3666f603...",
                            "polygon": "0x58c61AeE...",
                            "bsc": "0x3d4Cc8A6..."
                        }
                    },
                    {
                        "name": "Multichain",
                        "contracts": {
                            "ethereum": "0x6b7a8789...",
                            "polygon": "0x4f3Aff3A...",
                            "bsc": "0xd1C5966f..."
                        }
                    }
                ]
            }
    
    def create_sample_network(self):
        """
        샘플 멀티체인 네트워크 생성
        """
        print("🔨 샘플 크로스체인 네트워크 생성 중...\n")
        
        # 각 체인에 토큰/지갑 생성
        tokens_per_chain = 20
        wallets_per_token = 50
        
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
                    
                    # 거래 엣지
                    if random.random() > 0.3:
                        self.unified_graph.add_edge(
                            wallet_node,
                            token_node,
                            type='transaction',
                            value=random.uniform(100, 100000),
                            timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
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
        
        sample_wallets = random.sample(wallet_nodes, min(100, len(wallet_nodes)))
        
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
                    value=random.uniform(1000, 50000)
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
            and self.unified_graph.nodes[n].get('risk_score', 0) > 70
        ]
        
        for token in high_risk_tokens[:5]:  # 상위 5개만
            # 해당 토큰에서 브릿지로 가는 경로
            paths = self._trace_cross_chain_path(token, max_depth=4)
            
            for path in paths:
                if len(set([self.unified_graph.nodes[n]['chain'] 
                           for n in path])) >= 2:  # 2개 이상 체인
                    
                    suspicion_score = self._calculate_path_suspicion(path)
                    
                    if suspicion_score > 60:
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
            print(f"    경로: {' → '.join([n[:20] for n in path_info['path'][:4]])}")
            print()
        
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
        
        print(f"크로스체인 연결: {cross_chain_edges}개")
        print(f"전체 연결 대비 비율: {cross_chain_edges/self.unified_graph.number_of_edges()*100:.1f}%")


def main():
    print("=" * 70)
    print("🌐 크로스체인 AML 시스템 - 실전 데모")
    print("=" * 70)
    print()
    print("이 데모는 실제 데이터 없이 크로스체인 확장 개념을 보여줍니다.")
    print()
    
    # 1. 초기화
    demo = CrossChainDemo()
    
    # 2. 샘플 네트워크 생성
    demo.create_sample_network()
    
    # 3. 크로스체인 연결 추가
    demo.add_cross_chain_connections()
    
    # 4. 통계
    demo.generate_statistics()
    
    # 5. 의심 경로 탐지
    suspicious = demo.find_suspicious_cross_chain_paths()
    
    print("\n" + "=" * 70)
    print("💡 실제 구현 시 필요한 것들")
    print("=" * 70)
    print()
    print("1. 📦 브릿지 거래 데이터 수집")
    print("   - Etherscan, Polygonscan, BscScan API")
    print("   - 브릿지 컨트랙트 이벤트 로그")
    print()
    print("2. ⏰ 시간 기반 매칭")
    print("   - 브릿지 입금 후 5-30분 이내 출금 매칭")
    print("   - 금액 유사도 체크 (수수료 고려)")
    print()
    print("3. 🤖 지갑 클러스터링")
    print("   - 같은 시간대 활동 패턴")
    print("   - 거래 금액 유사성")
    print("   - 공통 거래 상대방")
    print()
    print("4. 📊 실시간 모니터링")
    print("   - Kafka/WebSocket 스트리밍")
    print("   - 의심 거래 즉시 알림")
    print()
    print("=" * 70)
    print("✅ 데모 완료!")
    print("=" * 70)


if __name__ == "__main__":
    main()

