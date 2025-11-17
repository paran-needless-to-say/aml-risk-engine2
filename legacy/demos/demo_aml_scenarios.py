"""Quick AML demo covering three scenarios using polygon contract sample."""
import pandas as pd
import networkx as nx
from pathlib import Path
from datetime import datetime
import numpy as np

DATA_PATH = Path("data/transactions/polygon/0x1ce4a2c355f0dcc24e32a9af19f1836d6f4f98ae.csv")

SCENARIO_OUTPUT = []


def load_transactions(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df['block_number'] = pd.to_numeric(df['block_number'], errors='coerce')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    df['from'] = df['from'].astype(str).str.lower()
    df['to'] = df['to'].astype(str).str.lower()
    df = df.dropna(subset=['from', 'to', 'timestamp'])
    df = df[df['from'] != df['to']]
    df = df.drop_duplicates(subset=['transaction_hash'])
    return df


def build_graph(df: pd.DataFrame) -> nx.DiGraph:
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['from'], row['to'], block=row['block_number'], value=row['value'], ts=row['timestamp'])
    return G


def scenario_listing_risk(G: nx.DiGraph):
    density = nx.density(G)
    reciprocity = nx.overall_reciprocity(G) or 0.0
    try:
        assortativity = nx.degree_assortativity_coefficient(G)
    except Exception:
        assortativity = 0.0

    risk_flags = []
    if reciprocity < 0.1:
        risk_flags.append("양방향 거래 부족")
    if density < 0.01:
        risk_flags.append("희박한 네트워크")
    if assortativity < -0.2:
        risk_flags.append("허브-말단 구조")

    score = 20
    if risk_flags:
        score = 80
    result = {
        "scenario": "Scenario 1: 상장 심사 리스크 평가",
        "density": density,
        "reciprocity": reciprocity,
        "assortativity": assortativity,
        "risk_flags": risk_flags,
        "score": score,
    }
    SCENARIO_OUTPUT.append(result)
    print("[Scenario 1] Listing Risk")
    print(f"Density: {density:.4f}, Reciprocity: {reciprocity:.4f}, Assortativity: {assortativity:.4f}")
    if risk_flags:
        print("⚠️ Flags:", ", ".join(risk_flags))
    else:
        print("✅ 주요 리스크 없음")
    print(f"→ 상장 위험 점수: {score}/100\n")


def scenario_realtime_alert(df: pd.DataFrame, G: nx.DiGraph):
    df_sorted = df.sort_values('timestamp')
    split_ts = df_sorted['timestamp'].quantile(0.8)
    baseline = df_sorted[df_sorted['timestamp'] <= split_ts]
    recent = df_sorted[df_sorted['timestamp'] > split_ts]

    def fanout(frame):
        return frame.groupby('from')['to'].nunique()

    baseline_fanout = fanout(baseline)
    recent_fanout = fanout(recent)
    combined = pd.concat([baseline_fanout.rename('baseline'), recent_fanout.rename('recent')], axis=1).fillna(0)
    if not combined.empty:
        combined['delta_pct'] = np.where(combined['baseline'] > 0, (combined['recent'] - combined['baseline']) / combined['baseline'], np.nan)
        surge_accounts = combined[combined['delta_pct'] > 1.0].sort_values('delta_pct', ascending=False)
    else:
        surge_accounts = pd.DataFrame()

    alert = not surge_accounts.empty
    top_accounts = surge_accounts.head(3).index.tolist()
    result = {
        "scenario": "Scenario 2: 실시간 이상거래 감지",
        "alert": alert,
        "top_accounts": top_accounts,
    }
    SCENARIO_OUTPUT.append(result)

    print("[Scenario 2] Real-time Alert")
    if alert:
        print("⚠️ Fan-out 급증 주소 발견 →", ", ".join(top_accounts))
    else:
        print("✅ Fan-out 급증 패턴 없음")
    print()


def scenario_investigation(G: nx.DiGraph):
    UG = G.to_undirected()
    degree = dict(G.out_degree())
    betweenness = nx.betweenness_centrality(UG, k=min(50, UG.number_of_nodes()))

    try:
        communities = list(nx.algorithms.community.greedy_modularity_communities(UG))
    except Exception:
        communities = []

    top_degree = sorted(degree.items(), key=lambda x: x[1], reverse=True)[:5]
    top_bet = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]

    result = {
        "scenario": "Scenario 3: 조사/추적",
        "top_degree": top_degree,
        "top_betweenness": top_bet,
        "num_communities": len(communities),
    }
    SCENARIO_OUTPUT.append(result)

    print("[Scenario 3] Investigation Support")
    print("Top degree nodes:")
    for addr, val in top_degree:
        print(f"  - {addr[:10]}… : out-degree {val}")
    print("Top betweenness nodes:")
    for addr, val in top_bet:
        print(f"  - {addr[:10]}… : betweenness {val:.4f}")
    print(f"Detected communities: {len(communities)}\n")


def main():
    df = load_transactions(DATA_PATH)
    G = build_graph(df)

    scenario_listing_risk(G)
    scenario_realtime_alert(df, G)
    scenario_investigation(G)

    report_lines = ["# AML Scenario Demo Summary", ""]
    for item in SCENARIO_OUTPUT:
        report_lines.append(f"## {item['scenario']}")
        for key, value in item.items():
            if key == 'scenario':
                continue
            report_lines.append(f"- **{key}**: {value}")
        report_lines.append("")
    Path("reports").mkdir(exist_ok=True)
    (Path("reports") / "demo_scenarios.md").write_text("\n".join(report_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
