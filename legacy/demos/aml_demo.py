"""
실제 AML 시스템 결과 데모
이 프로젝트로 만든 AML이 어떻게 작동하는지 보여줌

Usage:
    python aml_demo.py
        → 사전 정의된 3가지 예시 결과를 출력 (기존 데모 모드)

    python aml_demo.py --chain <bsc|ethereum|polygon> --contract <contract_address>
        → data/transactions/<chain>/<contract>.csv 를 로드해 실데이터 기반으로 분석
"""

import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx
from networkx.algorithms import approximation as nx_approx

class ExplainableAMLDetector:
    """
    설명 가능한 AML 탐지 시스템
    """
    
    def __init__(self):
        # 임계값 설정 (실제 데이터 분석 후 설정)
        self.thresholds = {
            'density_high': 0.8,
            'density_low': 0.01,
            'reciprocity_low': 0.1,
            'assortativity_neg': -0.3,
            'clustering_low': 0.05,
            'diameter_high': 15,
            'nodes_high': 10000,
            'edges_ratio_high': 3
        }
        
        # 시나리오 정의
        self.scenarios = {
            'S1_LAYERING': {
                'name': '레이어링 (Layering)',
                'description': '자금을 여러 계좌로 복잡하게 이동시켜 출처 은폐',
                'pattern': ['density_high', 'diameter_high', 'clustering_low'],
                'severity': 'HIGH',
                'sar_required': True  # SAR 제출 필요
            },
            'S2_SMURFING': {
                'name': '스머핑 (Smurfing)',
                'description': '소액을 다수 계좌로 분산하여 탐지 회피',
                'pattern': ['nodes_high', 'edges_ratio_high', 'reciprocity_low'],
                'severity': 'HIGH',
                'sar_required': True
            },
            'S3_RAPID_MOVEMENT': {
                'name': '급속 자금 이동',
                'description': '짧은 시간에 여러 계좌로 빠른 자금 흐름',
                'pattern': ['reciprocity_low', 'diameter_high'],
                'severity': 'MEDIUM',
                'sar_required': False
            },
            'S4_MIXER_PATTERN': {
                'name': '믹서/텀블러 사용',
                'description': '암호화폐 믹싱 서비스 사용 의심',
                'pattern': ['assortativity_neg', 'clustering_low', 'nodes_high'],
                'severity': 'HIGH',
                'sar_required': True
            },
            'S5_PUMP_DUMP': {
                'name': 'Pump & Dump',
                'description': '시세 조작 의심 패턴',
                'pattern': ['density_low', 'nodes_high', 'edges_ratio_high'],
                'severity': 'MEDIUM',
                'sar_required': False
            }
        }
    
    def analyze_token(self, token_address, graph_metrics, transaction_history=None):
        """
        토큰 분석 및 리스크 평가
        
        Returns: 완전한 AML 보고서
        """
        
        # 1. 피처 이상 탐지
        anomalies = self._check_feature_anomalies(graph_metrics)
        
        # 2. 시나리오 매칭
        matched_scenarios = self._match_scenarios(anomalies)
        
        # 3. AI 모델 점수 (시뮬레이션)
        ai_score = self._simulate_ai_model(graph_metrics)
        
        # 4. 최종 리스크 점수 계산
        risk_score = self._calculate_final_risk_score(matched_scenarios, ai_score)
        
        # 5. 설명 생성
        explanation = self._generate_detailed_explanation(
            graph_metrics, anomalies, matched_scenarios, ai_score, risk_score
        )
        
        # 6. 권장 조치
        recommendations = self._generate_recommendations(risk_score, matched_scenarios)
        
        # 7. 이유 코드 생성
        reason_code = self._generate_reason_code(matched_scenarios, anomalies)
        
        return {
            'token_address': token_address,
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'ai_model_score': ai_score,
            'matched_scenarios': matched_scenarios,
            'anomalous_features': anomalies,
            'explanation': explanation,
            'reason_code': reason_code,
            'recommendations': recommendations,
            'requires_sar': any(s.get('sar_required', False) for s in matched_scenarios),
            'graph_metrics': graph_metrics
        }
    
    def _check_feature_anomalies(self, metrics):
        """피처 이상 탐지"""
        anomalies = []
        
        if metrics['Density'] > self.thresholds['density_high']:
            anomalies.append('density_high')
        elif metrics['Density'] < self.thresholds['density_low']:
            anomalies.append('density_low')
        
        if metrics['Reciprocity'] < self.thresholds['reciprocity_low']:
            anomalies.append('reciprocity_low')
        
        if metrics['Assortativity'] < self.thresholds['assortativity_neg']:
            anomalies.append('assortativity_neg')
        
        if metrics['Clustering_Coefficient'] < self.thresholds['clustering_low']:
            anomalies.append('clustering_low')
        
        if metrics['Effective_Diameter'] > self.thresholds['diameter_high']:
            anomalies.append('diameter_high')
        
        if metrics['Num_nodes'] > self.thresholds['nodes_high']:
            anomalies.append('nodes_high')
        
        edge_ratio = metrics['Num_edges'] / max(metrics['Num_nodes'], 1)
        if edge_ratio > self.thresholds['edges_ratio_high']:
            anomalies.append('edges_ratio_high')
        
        return anomalies
    
    def _match_scenarios(self, anomalies):
        """시나리오 매칭"""
        matched = []
        anomaly_set = set(anomalies)
        
        for scenario_id, scenario_data in self.scenarios.items():
            pattern_set = set(scenario_data['pattern'])
            match_count = len(anomaly_set & pattern_set)
            match_ratio = match_count / len(pattern_set)
            
            if match_ratio >= 0.5:  # 50% 이상 매칭
                matched.append({
                    'id': scenario_id,
                    'name': scenario_data['name'],
                    'description': scenario_data['description'],
                    'severity': scenario_data['severity'],
                    'confidence': match_ratio * 100,
                    'matched_features': list(anomaly_set & pattern_set),
                    'sar_required': scenario_data.get('sar_required', False)
                })
        
        matched.sort(key=lambda x: x['confidence'], reverse=True)
        return matched
    
    def _simulate_ai_model(self, metrics):
        """
        AI 모델 점수 시뮬레이션
        실제로는 학습된 DOMINANT, GAE 등의 모델 사용
        """
        # 여러 피처를 종합하여 이상 점수 계산
        score = 0
        
        # 밀집도 기반
        if metrics['Density'] > 0.7 or metrics['Density'] < 0.02:
            score += 0.25
        
        # 네트워크 구조 기반
        if metrics['Assortativity'] < -0.2:
            score += 0.2
        
        # 거래 패턴 기반
        if metrics['Reciprocity'] < 0.15:
            score += 0.25
        
        # 규모 기반
        if metrics['Num_nodes'] > 5000:
            score += 0.15
        
        # 클러스터링 기반
        if metrics['Clustering_Coefficient'] < 0.1:
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_final_risk_score(self, scenarios, ai_score):
        """최종 리스크 점수 (0-100)"""
        
        # AI 모델 점수 (50%)
        score = ai_score * 50
        
        # 시나리오 매칭 (50%)
        if scenarios:
            severity_weights = {'HIGH': 50, 'MEDIUM': 35, 'LOW': 20}
            scenario_score = 0
            
            for scenario in scenarios:
                weight = severity_weights.get(scenario['severity'], 20)
                scenario_score += weight * (scenario['confidence'] / 100)
            
            score += min(scenario_score, 50)
        
        return min(score, 100)
    
    def _get_risk_level(self, score):
        """리스크 레벨"""
        if score >= 75:
            return 'CRITICAL'
        elif score >= 50:
            return 'HIGH'
        elif score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_detailed_explanation(self, metrics, anomalies, scenarios, ai_score, risk_score):
        """상세 설명"""
        lines = []
        
        lines.append("=" * 70)
        lines.append("🔍 AML 분석 결과 보고서")
        lines.append("=" * 70)
        
        lines.append(f"\n📊 **종합 리스크 평가**")
        lines.append(f"  • 최종 리스크 점수: {risk_score:.1f}/100")
        lines.append(f"  • 리스크 레벨: {self._get_risk_level(risk_score)}")
        lines.append(f"  • AI 모델 이상 점수: {ai_score:.2f}")
        
        if scenarios:
            lines.append(f"\n⚠️  **탐지된 의심 시나리오 ({len(scenarios)}건)**")
            for i, scenario in enumerate(scenarios[:3], 1):
                lines.append(f"\n  [{i}] {scenario['name']}")
                lines.append(f"      신뢰도: {scenario['confidence']:.0f}%")
                lines.append(f"      심각도: {scenario['severity']}")
                lines.append(f"      설명: {scenario['description']}")
                if scenario['sar_required']:
                    lines.append(f"      🚨 SAR 제출 필요")
        
        if anomalies:
            lines.append(f"\n📈 **이상 탐지된 그래프 메트릭 ({len(anomalies)}개)**")
            
            feature_details = {
                'density_high': (
                    f"밀집도 과도하게 높음: {metrics['Density']:.4f}",
                    "→ 특정 지갑들 간 집중된 거래, 순환 거래 의심"
                ),
                'density_low': (
                    f"밀집도 매우 낮음: {metrics['Density']:.6f}",
                    "→ 불규칙한 거래 패턴, Pump & Dump 의심"
                ),
                'reciprocity_low': (
                    f"양방향 거래 비율 낮음: {metrics['Reciprocity']:.3f}",
                    "→ 일방적 자금 흐름, 레이어링 의심"
                ),
                'assortativity_neg': (
                    f"음수 연결성: {metrics['Assortativity']:.3f}",
                    "→ 비정상적 네트워크 구조, 믹서 사용 의심"
                ),
                'clustering_low': (
                    f"낮은 클러스터링: {metrics['Clustering_Coefficient']:.3f}",
                    "→ 분산된 거래 패턴, 스머핑 가능성"
                ),
                'diameter_high': (
                    f"네트워크 직경 큼: {metrics['Effective_Diameter']:.1f}",
                    "→ 넓게 확산된 거래, 복잡한 자금 이동"
                ),
                'nodes_high': (
                    f"비정상적으로 많은 지갑: {metrics['Num_nodes']:,}개",
                    "→ 대규모 네트워크, 조직적 활동 의심"
                ),
                'edges_ratio_high': (
                    f"높은 거래 빈도: 평균 {metrics['Num_edges']/metrics['Num_nodes']:.1f}회/지갑",
                    "→ 과도한 거래 활동"
                )
            }
            
            for anomaly in anomalies:
                if anomaly in feature_details:
                    detail, interpretation = feature_details[anomaly]
                    lines.append(f"\n  • {detail}")
                    lines.append(f"    {interpretation}")
        
        lines.append(f"\n📋 **상세 그래프 메트릭**")
        lines.append(f"  • 노드 수 (지갑): {metrics['Num_nodes']:,}개")
        lines.append(f"  • 엣지 수 (거래): {metrics['Num_edges']:,}개")
        lines.append(f"  • 밀집도 (Density): {metrics['Density']:.6f}")
        lines.append(f"  • 연결성 (Assortativity): {metrics['Assortativity']:.4f}")
        lines.append(f"  • 양방향성 (Reciprocity): {metrics['Reciprocity']:.4f}")
        lines.append(f"  • 네트워크 직경 (Effective Diameter): {metrics['Effective_Diameter']:.2f}")
        lines.append(f"  • 클러스터링 계수: {metrics['Clustering_Coefficient']:.4f}")
        
        return "\n".join(lines)
    
    def _generate_recommendations(self, risk_score, scenarios):
        """권장 조치"""
        recommendations = []
        
        if risk_score >= 75:
            recommendations.append("🚨 즉시 조치 필요")
            recommendations.append("  1. 해당 토큰의 모든 거래 즉시 모니터링 강화")
            recommendations.append("  2. 주요 연결 지갑 식별 및 추적")
            recommendations.append("  3. SAR (Suspicious Activity Report) 제출 검토")
            recommendations.append("  4. 필요시 거래 일시 제한 조치")
            recommendations.append("  5. 법 집행 기관 보고 검토")
            
        elif risk_score >= 50:
            recommendations.append("⚠️  높은 주의 필요")
            recommendations.append("  1. 72시간 집중 모니터링")
            recommendations.append("  2. 거래 패턴 상세 분석")
            recommendations.append("  3. 관련 지갑들의 추가 조사")
            recommendations.append("  4. 내부 보고서 작성")
            
        elif risk_score >= 30:
            recommendations.append("📋 일반 모니터링")
            recommendations.append("  1. 정기 모니터링 대상 추가")
            recommendations.append("  2. 월간 리뷰 시 재평가")
            
        else:
            recommendations.append("✅ 정상 범위")
            recommendations.append("  1. 표준 모니터링 유지")
        
        # 시나리오별 추가 권장사항
        for scenario in scenarios:
            if scenario['id'] == 'S1_LAYERING':
                recommendations.append("\n💡 레이어링 대응:")
                recommendations.append("  • 자금 흐름 경로 완전 추적")
                recommendations.append("  • 최종 목적지 지갑 식별")
                
            elif scenario['id'] == 'S2_SMURFING':
                recommendations.append("\n💡 스머핑 대응:")
                recommendations.append("  • 소액 거래 패턴 분석")
                recommendations.append("  • 시간대별 거래 집중도 확인")
                
            elif scenario['id'] == 'S4_MIXER_PATTERN':
                recommendations.append("\n💡 믹서 사용 대응:")
                recommendations.append("  • 알려진 믹서 서비스와 비교")
                recommendations.append("  • 입출금 패턴 상세 분석")
        
        return "\n".join(recommendations)
    
    def _generate_reason_code(self, scenarios, anomalies):
        """시스템 연동용 이유 코드"""
        if not scenarios:
            return "R000_NORMAL"
        
        # 주 시나리오
        primary = scenarios[0]['id']
        
        # 이상 피처 코드
        feature_codes = {
            'density_high': 'DH',
            'density_low': 'DL',
            'reciprocity_low': 'RL',
            'assortativity_neg': 'AN',
            'clustering_low': 'CL',
            'diameter_high': 'DH',
            'nodes_high': 'NH',
            'edges_ratio_high': 'EH'
        }
        
        feature_str = ''.join([feature_codes.get(a, '') for a in anomalies[:3]])
        
        return f"{primary}_{feature_str}"


def _load_transactions(chain, contract, transactions_dir):
    tx_path = Path(transactions_dir) / chain / f"{contract}.csv"
    if not tx_path.exists():
        raise FileNotFoundError(f"Transaction file not found: {tx_path}")

    df = pd.read_csv(tx_path)
    missing_columns = [col for col in ["from", "to"] if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns {missing_columns} in {tx_path}")

    return df


def _build_graph_from_transactions(df):
    G = nx.DiGraph()
    for _, row in df.iterrows():
        src = row["from"]
        dst = row["to"]
        if pd.isna(src) or pd.isna(dst):
            continue
        G.add_edge(src, dst)
    return G


def _safe_value(value, default=0.0):
    if value is None:
        return default
    if isinstance(value, float) and np.isnan(value):
        return default
    return float(value)


def compute_metrics_from_transactions(chain, contract, transactions_dir="data/transactions"):
    df = _load_transactions(chain, contract, transactions_dir)
    G = _build_graph_from_transactions(df)

    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()

    if num_nodes == 0:
        return {
            "Num_nodes": 0,
            "Num_edges": 0,
            "Density": 0.0,
            "Assortativity": 0.0,
            "Reciprocity": 0.0,
            "Effective_Diameter": 0.0,
            "Clustering_Coefficient": 0.0,
        }

    density = nx.density(G)
    try:
        assortativity = nx.degree_assortativity_coefficient(G)
    except Exception:
        assortativity = 0.0

    reciprocity = _safe_value(nx.overall_reciprocity(G))

    undirected_graph = G.to_undirected()
    if undirected_graph.number_of_edges() == 0 or undirected_graph.number_of_nodes() <= 1:
        effective_diameter = 0.0
        clustering_coefficient = 0.0
    else:
        largest_component_nodes = max(nx.connected_components(undirected_graph), key=len)
        largest_component = undirected_graph.subgraph(largest_component_nodes).copy()

        try:
            effective_diameter = float(nx_approx.diameter(largest_component))
        except Exception:
            effective_diameter = float(len(largest_component_nodes) - 1)

        try:
            clustering_coefficient = nx.average_clustering(largest_component)
        except Exception:
            clustering_coefficient = 0.0

    return {
        "Num_nodes": num_nodes,
        "Num_edges": num_edges,
        "Density": _safe_value(density, 0.0),
        "Assortativity": _safe_value(assortativity, 0.0),
        "Reciprocity": _safe_value(reciprocity, 0.0),
        "Effective_Diameter": _safe_value(effective_diameter, 0.0),
        "Clustering_Coefficient": _safe_value(clustering_coefficient, 0.0),
    }


def run_real_analysis(chain, contract, transactions_dir="data/transactions"):
    detector = ExplainableAMLDetector()
    try:
        metrics = compute_metrics_from_transactions(chain, contract, transactions_dir)
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        return
    except ValueError as exc:
        print(f"❌ 데이터 형식 오류: {exc}")
        return

    result = detector.analyze_token(contract, metrics)

    print("\n" + "=" * 70)
    print(f"🔍 실데이터 AML 분석 - {chain}/{contract}")
    print("=" * 70)
    print(result["explanation"])
    print(f"\n이유 코드: {result['reason_code']}")
    print(f"SAR 제출 필요: {'예 🚨' if result['requires_sar'] else '아니오'}")
    print(f"\n{result['recommendations']}")


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Explainable AML detector demo. "
        "Run without arguments for canned examples or provide --chain and --contract to analyze real data."
    )
    parser.add_argument(
        "--chain",
        choices=["bsc", "ethereum", "polygon"],
        help="Chain name corresponding to subdirectory under data/transactions/",
    )
    parser.add_argument(
        "--contract",
        help="Contract address (CSV filename without extension) to analyze.",
    )
    parser.add_argument(
        "--transactions-dir",
        default="data/transactions",
        help="Root directory containing chain subdirectories with transaction CSV files.",
    )
    return parser


def run_demo():
    """실제 사용 예시 데모"""
    
    print("\n" + "=" * 70)
    print("🏦 블록체인 AML 시스템 - 실제 결과 예시")
    print("=" * 70)
    
    detector = ExplainableAMLDetector()
    
    # 예시 1: 정상 토큰
    print("\n\n[예시 1] 정상 토큰")
    print("-" * 70)
    normal_token = {
        'Num_nodes': 234,
        'Num_edges': 567,
        'Density': 0.15,
        'Assortativity': 0.12,
        'Reciprocity': 0.45,
        'Effective_Diameter': 5.2,
        'Clustering_Coefficient': 0.32
    }
    
    result1 = detector.analyze_token('0x1234...Normal', normal_token)
    print(result1['explanation'])
    print(f"\n이유 코드: {result1['reason_code']}")
    print(f"\n{result1['recommendations']}")
    
    # 예시 2: 레이어링 의심
    print("\n\n" + "=" * 70)
    print("[예시 2] 레이어링 의심 토큰")
    print("-" * 70)
    layering_token = {
        'Num_nodes': 8543,
        'Num_edges': 34219,
        'Density': 0.87,
        'Assortativity': -0.15,
        'Reciprocity': 0.08,
        'Effective_Diameter': 18.7,
        'Clustering_Coefficient': 0.04
    }
    
    result2 = detector.analyze_token('0xABCD...Suspicious', layering_token)
    print(result2['explanation'])
    print(f"\n이유 코드: {result2['reason_code']}")
    print(f"SAR 제출 필요: {'예 🚨' if result2['requires_sar'] else '아니오'}")
    print(f"\n{result2['recommendations']}")
    
    # 예시 3: 스머핑 의심
    print("\n\n" + "=" * 70)
    print("[예시 3] 스머핑 의심 토큰")
    print("-" * 70)
    smurfing_token = {
        'Num_nodes': 15234,
        'Num_edges': 52891,
        'Density': 0.03,
        'Assortativity': 0.05,
        'Reciprocity': 0.07,
        'Effective_Diameter': 12.3,
        'Clustering_Coefficient': 0.18
    }
    
    result3 = detector.analyze_token('0xDEF0...Smurfing', smurfing_token)
    print(result3['explanation'])
    print(f"\n이유 코드: {result3['reason_code']}")
    print(f"SAR 제출 필요: {'예 🚨' if result3['requires_sar'] else '아니오'}")
    print(f"\n{result3['recommendations']}")
    
    # 요약 테이블
    print("\n\n" + "=" * 70)
    print("📊 분석 결과 요약")
    print("=" * 70)
    print(f"{'토큰':20} {'리스크 점수':12} {'레벨':10} {'주요 시나리오':25} {'SAR':5}")
    print("-" * 70)
    
    for result in [result1, result2, result3]:
        token = result['token_address'][:20].ljust(20)
        score = f"{result['risk_score']:.1f}/100".ljust(12)
        level = result['risk_level'].ljust(10)
        scenario = (result['matched_scenarios'][0]['name'][:25] if result['matched_scenarios'] else '-').ljust(25)
        sar = '필요' if result['requires_sar'] else '-'
        
        print(f"{token} {score} {level} {scenario} {sar}")


if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.chain and args.contract:
        run_real_analysis(args.chain, args.contract, args.transactions_dir)
    elif args.chain or args.contract:
        parser.error("Both --chain and --contract must be provided to analyze real data.")
    else:
        run_demo()

