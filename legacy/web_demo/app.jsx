const { useMemo, useState, useEffect, useRef } = React;

const MOCK = {
  Ethereum: [
    {
      chain: "ethereum",
      contract: "0x1154...220f",
      name: "ETH-Rapid",
      nodes: 3164,
      edges: 8149,
      density: 0.01943,
      assortativity: 0.0,
      reciprocity: 0.0,
      clustering: 0.0,
      effDiameter: 20,
      riskScore: 8.1,
      anomalyScore: 0.71,
      reasons: [
        { key: "reciprocity_low", label: "양방향 거래 비율 낮음" },
        { key: "clustering_low", label: "클러스터링 없음" },
        { key: "fanout_spike", label: "팬아웃 급증" },
      ],
      neighbors: [
        { token: "0xDeF...9a1", jaccard: 0.31 },
        { token: "0xAaB...11c", jaccard: 0.24 },
      ],
      samples: [
        { tx: "0xabc1", ts: 1712345678, amt: 93210.4 },
        { tx: "0xabc2", ts: 1712347777, amt: 4012.1 },
      ],
      graph: {
        nodes: [
          {
            id: "hub",
            label: "Hub Wallet",
            size: 12,
            color: "#ef4444",
            x: 0,
            y: 0,
          },
          {
            id: "leaf1",
            label: "Leaf A",
            size: 6,
            color: "#f97316",
            x: 1,
            y: 1,
          },
          {
            id: "leaf2",
            label: "Leaf B",
            size: 4,
            color: "#f97316",
            x: -1,
            y: 1,
          },
          {
            id: "leaf3",
            label: "Leaf C",
            size: 3,
            color: "#f97316",
            x: 1.2,
            y: -1,
          },
          {
            id: "bridge",
            label: "Bridge Wallet",
            size: 7,
            color: "#0ea5e9",
            x: -1.2,
            y: -1,
          },
          {
            id: "mixer",
            label: "Mixer",
            size: 5,
            color: "#14b8a6",
            x: 0.2,
            y: -1.8,
          },
        ],
        edges: [
          { id: "e1", source: "hub", target: "leaf1" },
          { id: "e2", source: "hub", target: "leaf2" },
          { id: "e3", source: "hub", target: "leaf3" },
          { id: "e4", source: "hub", target: "bridge" },
          { id: "e5", source: "bridge", target: "mixer" },
          { id: "e6", source: "mixer", target: "leaf1" },
          { id: "e7", source: "mixer", target: "leaf2" },
        ],
      },
    },
    {
      chain: "ethereum",
      contract: "0x8a24...cd3",
      name: "ETH-Clustered",
      nodes: 820,
      edges: 1290,
      density: 0.0033,
      assortativity: -0.21,
      reciprocity: 0.18,
      clustering: 0.16,
      effDiameter: 9,
      riskScore: 5.0,
      anomalyScore: 0.44,
      reasons: [{ key: "assortativity_neg", label: "음의 연결성향" }],
      neighbors: [{ token: "0x884...ff0", jaccard: 0.12 }],
      samples: [{ tx: "0x9de1", ts: 1711111111, amt: 154.2 }],
      graph: {
        nodes: [
          {
            id: "core",
            label: "Core Cluster",
            size: 10,
            color: "#6366f1",
            x: 0,
            y: 0,
          },
          {
            id: "peer1",
            label: "Peer 1",
            size: 5,
            color: "#a855f7",
            x: 1,
            y: 0.4,
          },
          {
            id: "peer2",
            label: "Peer 2",
            size: 5,
            color: "#a855f7",
            x: -0.8,
            y: 0.6,
          },
          {
            id: "peer3",
            label: "Peer 3",
            size: 5,
            color: "#a855f7",
            x: 0.6,
            y: -0.9,
          },
          {
            id: "peer4",
            label: "Peer 4",
            size: 5,
            color: "#a855f7",
            x: -0.6,
            y: -0.8,
          },
        ],
        edges: [
          { id: "ec1", source: "core", target: "peer1" },
          { id: "ec2", source: "core", target: "peer2" },
          { id: "ec3", source: "core", target: "peer3" },
          { id: "ec4", source: "core", target: "peer4" },
          { id: "ec5", source: "peer1", target: "peer2" },
          { id: "ec6", source: "peer2", target: "peer3" },
          { id: "ec7", source: "peer3", target: "peer4" },
        ],
      },
    },
    {
      chain: "ethereum",
      contract: "0x4f21...77de",
      name: "ETH-BridgeNet",
      nodes: 1_540,
      edges: 3_980,
      density: 0.00335,
      assortativity: -0.402,
      reciprocity: 0.064,
      clustering: 0.072,
      effDiameter: 11,
      riskScore: 7.4,
      anomalyScore: 0.62,
      reasons: [
        { key: "bridge_spike", label: "브릿지 유입 급증" },
        { key: "low_recip", label: "일방향 거래 다수" },
      ],
      neighbors: [
        { token: "0x99c...aee", jaccard: 0.23 },
        { token: "0x11f...9d1", jaccard: 0.17 },
      ],
      samples: [
        { tx: "0xbridge1", ts: 1712500000, amt: 73_210.11 },
        { tx: "0xbridge2", ts: 1712503600, amt: 18_420.55 },
      ],
      graph: {
        nodes: [
          {
            id: "ethHub",
            label: "Bridge Hub",
            size: 11,
            color: "#ef4444",
            x: 0,
            y: 0,
          },
          {
            id: "ethFan1",
            label: "Fanout 1",
            size: 6,
            color: "#f97316",
            x: 1.3,
            y: 0.5,
          },
          {
            id: "ethFan2",
            label: "Fanout 2",
            size: 6,
            color: "#f97316",
            x: -1.1,
            y: 0.7,
          },
          {
            id: "ethBridge",
            label: "L2 Bridge",
            size: 7,
            color: "#2563eb",
            x: 0.8,
            y: -1.2,
          },
          {
            id: "ethMixer",
            label: "Mixer",
            size: 6,
            color: "#14b8a6",
            x: -0.8,
            y: -1.1,
          },
        ],
        edges: [
          { id: "eb1", source: "ethHub", target: "ethFan1" },
          { id: "eb2", source: "ethHub", target: "ethFan2" },
          { id: "eb3", source: "ethHub", target: "ethBridge" },
          { id: "eb4", source: "ethBridge", target: "ethMixer" },
          { id: "eb5", source: "ethMixer", target: "ethFan1" },
        ],
      },
    },
    {
      chain: "ethereum",
      contract: "0x6dd3...12ba",
      name: "ETH-StableFlow",
      nodes: 980,
      edges: 1_620,
      density: 0.00337,
      assortativity: 0.045,
      reciprocity: 0.398,
      clustering: 0.362,
      effDiameter: 8,
      riskScore: 3.6,
      anomalyScore: 0.29,
      reasons: [{ key: "balanced", label: "균형 잡힌 유동성" }],
      neighbors: [{ token: "0x22b...44d", jaccard: 0.09 }],
      samples: [
        { tx: "0xsf1", ts: 1711900000, amt: 4_210.22 },
        { tx: "0xsf2", ts: 1711988200, amt: 1_120.76 },
      ],
      graph: {
        nodes: [
          {
            id: "stableCore",
            label: "Stable Core",
            size: 9,
            color: "#2563eb",
            x: 0,
            y: 0,
          },
          {
            id: "stableA",
            label: "Stable A",
            size: 5,
            color: "#3b82f6",
            x: 1.0,
            y: 0.5,
          },
          {
            id: "stableB",
            label: "Stable B",
            size: 5,
            color: "#3b82f6",
            x: -1.1,
            y: 0.4,
          },
          {
            id: "stableC",
            label: "Stable C",
            size: 5,
            color: "#3b82f6",
            x: 0.6,
            y: -0.9,
          },
          {
            id: "stableD",
            label: "Stable D",
            size: 5,
            color: "#3b82f6",
            x: -0.5,
            y: -0.8,
          },
        ],
        edges: [
          { id: "es1", source: "stableCore", target: "stableA" },
          { id: "es2", source: "stableCore", target: "stableB" },
          { id: "es3", source: "stableCore", target: "stableC" },
          { id: "es4", source: "stableCore", target: "stableD" },
          { id: "es5", source: "stableA", target: "stableB" },
        ],
      },
    },
  ],
  Polygon: [
    {
      chain: "polygon",
      contract: "0x1ce4...f98ae",
      name: "POLY-LowRisk",
      nodes: 854,
      edges: 2243,
      density: 0.00379,
      assortativity: -0.4219,
      reciprocity: 0.3486,
      clustering: 0.3551,
      effDiameter: 7,
      riskScore: 2.3,
      anomalyScore: 0.45,
      reasons: [
        { key: "density_low", label: "밀도 낮음" },
        { key: "assortativity_neg", label: "음의 연결성향" },
      ],
      neighbors: [],
      samples: [],
      graph: {
        nodes: [
          {
            id: "p1",
            label: "Trader A",
            size: 6,
            color: "#0ea5e9",
            x: 0,
            y: 0,
          },
          {
            id: "p2",
            label: "Trader B",
            size: 4,
            color: "#0ea5e9",
            x: 1,
            y: 0.5,
          },
          {
            id: "p3",
            label: "Holder",
            size: 3,
            color: "#38bdf8",
            x: -1,
            y: 0.6,
          },
          {
            id: "p4",
            label: "Liquidity Pool",
            size: 5,
            color: "#22d3ee",
            x: 0.8,
            y: -0.9,
          },
          {
            id: "p5",
            label: "Collector",
            size: 4,
            color: "#22d3ee",
            x: -0.9,
            y: -0.8,
          },
        ],
        edges: [
          { id: "ep1", source: "p1", target: "p2" },
          { id: "ep2", source: "p1", target: "p3" },
          { id: "ep3", source: "p2", target: "p4" },
          { id: "ep4", source: "p3", target: "p5" },
          { id: "ep5", source: "p4", target: "p5" },
        ],
      },
    },
    {
      chain: "polygon",
      contract: "0x72d1...aa94f",
      name: "POLY-BridgeWatch",
      nodes: 1_240,
      edges: 3_420,
      density: 0.00443,
      assortativity: -0.312,
      reciprocity: 0.271,
      clustering: 0.298,
      effDiameter: 8,
      riskScore: 6.4,
      anomalyScore: 0.58,
      reasons: [
        { key: "bridge", label: "브릿지 허브 집중" },
        { key: "fanout", label: "팬아웃 급증" },
      ],
      neighbors: [
        { token: "0x98b...331", jaccard: 0.19 },
        { token: "0x40b...891", jaccard: 0.11 },
      ],
      samples: [
        { tx: "0xccd1", ts: 1712451234, amt: 50210.5 },
        { tx: "0xccd2", ts: 1712456234, amt: 9310.75 },
      ],
      graph: {
        nodes: [
          {
            id: "bridgeHub",
            label: "Bridge Hub",
            size: 10,
            color: "#22d3ee",
            x: 0,
            y: 0,
          },
          {
            id: "clusterA",
            label: "Cluster A",
            size: 5,
            color: "#0ea5e9",
            x: 1.2,
            y: 0.6,
          },
          {
            id: "clusterB",
            label: "Cluster B",
            size: 4,
            color: "#0ea5e9",
            x: -1.0,
            y: 0.8,
          },
          {
            id: "sink",
            label: "Liquidity Sink",
            size: 6,
            color: "#0284c7",
            x: 0.6,
            y: -1.1,
          },
          {
            id: "retail",
            label: "Retail Wallets",
            size: 5,
            color: "#38bdf8",
            x: -0.8,
            y: -1.2,
          },
        ],
        edges: [
          { id: "pb1", source: "bridgeHub", target: "clusterA" },
          { id: "pb2", source: "bridgeHub", target: "clusterB" },
          { id: "pb3", source: "bridgeHub", target: "sink" },
          { id: "pb4", source: "clusterA", target: "retail" },
          { id: "pb5", source: "sink", target: "retail" },
        ],
      },
    },
    {
      chain: "polygon",
      contract: "0x33fa...cc7d0",
      name: "POLY-Retail",
      nodes: 640,
      edges: 910,
      density: 0.00446,
      assortativity: 0.021,
      reciprocity: 0.412,
      clustering: 0.381,
      effDiameter: 6,
      riskScore: 3.2,
      anomalyScore: 0.31,
      reasons: [{ key: "sustained_liq", label: "LP 유동성 안정" }],
      neighbors: [],
      samples: [
        { tx: "0x11aa", ts: 1712001111, amt: 210.05 },
        { tx: "0x11ab", ts: 1712087654, amt: 92.4 },
      ],
      graph: {
        nodes: [
          {
            id: "retHub",
            label: "Retail Hub",
            size: 7,
            color: "#38bdf8",
            x: 0,
            y: 0,
          },
          {
            id: "retA",
            label: "Wallet A",
            size: 4,
            color: "#0ea5e9",
            x: 1.1,
            y: 0.4,
          },
          {
            id: "retB",
            label: "Wallet B",
            size: 4,
            color: "#0ea5e9",
            x: -1.0,
            y: 0.5,
          },
          {
            id: "retC",
            label: "Wallet C",
            size: 4,
            color: "#0ea5e9",
            x: 0.6,
            y: -0.9,
          },
          {
            id: "retD",
            label: "Wallet D",
            size: 4,
            color: "#0ea5e9",
            x: -0.6,
            y: -0.8,
          },
        ],
        edges: [
          { id: "pr1", source: "retHub", target: "retA" },
          { id: "pr2", source: "retHub", target: "retB" },
          { id: "pr3", source: "retHub", target: "retC" },
          { id: "pr4", source: "retHub", target: "retD" },
          { id: "pr5", source: "retA", target: "retB" },
        ],
      },
    },
  ],
  BSC: [
    {
      chain: "bsc",
      contract: "0x5ad8...406e6f",
      name: "BSC-Community",
      nodes: 403,
      edges: 1032,
      density: 0.00637,
      assortativity: -0.976,
      reciprocity: 0.5988,
      clustering: 0.7754,
      effDiameter: 4,
      riskScore: 4.8,
      anomalyScore: 0.52,
      reasons: [{ key: "assortativity_neg", label: "음의 연결성향" }],
      neighbors: [{ token: "0x777...bbb", jaccard: 0.21 }],
      samples: [{ tx: "0xb1", ts: 1712000000, amt: 100.0 }],
      graph: {
        nodes: [
          {
            id: "cluster1",
            label: "Community Hub",
            size: 8,
            color: "#f59e0b",
            x: 0,
            y: 0,
          },
          {
            id: "cluster2",
            label: "Community 2",
            size: 6,
            color: "#facc15",
            x: 1.1,
            y: 0.2,
          },
          {
            id: "cluster3",
            label: "Community 3",
            size: 6,
            color: "#facc15",
            x: -1.2,
            y: 0.3,
          },
          {
            id: "relay",
            label: "Relay",
            size: 5,
            color: "#fbbf24",
            x: 0.2,
            y: -1.0,
          },
          {
            id: "endpoint1",
            label: "Endpoint 1",
            size: 4,
            color: "#fde047",
            x: 1.3,
            y: -0.8,
          },
          {
            id: "endpoint2",
            label: "Endpoint 2",
            size: 4,
            color: "#fde047",
            x: -1.3,
            y: -0.7,
          },
        ],
        edges: [
          { id: "eb1", source: "cluster1", target: "cluster2" },
          { id: "eb2", source: "cluster1", target: "cluster3" },
          { id: "eb3", source: "cluster1", target: "relay" },
          { id: "eb4", source: "relay", target: "endpoint1" },
          { id: "eb5", source: "relay", target: "endpoint2" },
        ],
      },
    },
    {
      chain: "bsc",
      contract: "0x9012...66aa3",
      name: "BSC-MixerWatch",
      nodes: 1_850,
      edges: 4_320,
      density: 0.00252,
      assortativity: -0.624,
      reciprocity: 0.112,
      clustering: 0.041,
      effDiameter: 13,
      riskScore: 9.1,
      anomalyScore: 0.83,
      reasons: [
        { key: "mixer", label: "Mixer 다중 경유" },
        { key: "burst", label: "고속 유출" },
      ],
      neighbors: [
        { token: "0xabc...999", jaccard: 0.28 },
        { token: "0xdef...222", jaccard: 0.17 },
      ],
      samples: [
        { tx: "0xmix1", ts: 1712550000, amt: 125_400.32 },
        { tx: "0xmix2", ts: 1712553600, amt: 42_100.76 },
      ],
      graph: {
        nodes: [
          {
            id: "hubMix",
            label: "Mixer Hub",
            size: 12,
            color: "#f87171",
            x: 0,
            y: 0,
          },
          {
            id: "in1",
            label: "Ingress 1",
            size: 6,
            color: "#fb923c",
            x: 1.2,
            y: 0.6,
          },
          {
            id: "in2",
            label: "Ingress 2",
            size: 6,
            color: "#fb923c",
            x: -1.2,
            y: 0.7,
          },
          {
            id: "out1",
            label: "Off-ramp 1",
            size: 7,
            color: "#f59e0b",
            x: 0.7,
            y: -1.1,
          },
          {
            id: "out2",
            label: "Off-ramp 2",
            size: 6,
            color: "#facc15",
            x: -0.8,
            y: -1.1,
          },
        ],
        edges: [
          { id: "bm1", source: "in1", target: "hubMix" },
          { id: "bm2", source: "in2", target: "hubMix" },
          { id: "bm3", source: "hubMix", target: "out1" },
          { id: "bm4", source: "hubMix", target: "out2" },
          { id: "bm5", source: "out2", target: "out1" },
        ],
      },
    },
    {
      chain: "bsc",
      contract: "0x7b43...2c111",
      name: "BSC-DEXGuard",
      nodes: 980,
      edges: 2_110,
      density: 0.00439,
      assortativity: -0.105,
      reciprocity: 0.312,
      clustering: 0.251,
      effDiameter: 7,
      riskScore: 5.6,
      anomalyScore: 0.47,
      reasons: [
        { key: "router", label: "라우팅 허브 주도" },
        { key: "volume", label: "거래량 급등" },
      ],
      neighbors: [{ token: "0x1aa...bc3", jaccard: 0.09 }],
      samples: [{ tx: "0xguard1", ts: 1712100000, amt: 1_240.55 }],
      graph: {
        nodes: [
          {
            id: "dexCore",
            label: "DEX Core",
            size: 9,
            color: "#fbbf24",
            x: 0,
            y: 0,
          },
          {
            id: "pool1",
            label: "Pool 1",
            size: 6,
            color: "#f59e0b",
            x: 1.1,
            y: 0.4,
          },
          {
            id: "pool2",
            label: "Pool 2",
            size: 6,
            color: "#f59e0b",
            x: -1.0,
            y: 0.5,
          },
          {
            id: "arb",
            label: "Arb Bot",
            size: 5,
            color: "#fcd34d",
            x: 0.8,
            y: -1.0,
          },
          {
            id: "retailDex",
            label: "Retail Flow",
            size: 5,
            color: "#fde047",
            x: -0.7,
            y: -1.0,
          },
        ],
        edges: [
          { id: "bd1", source: "dexCore", target: "pool1" },
          { id: "bd2", source: "dexCore", target: "pool2" },
          { id: "bd3", source: "pool1", target: "arb" },
          { id: "bd4", source: "pool2", target: "retailDex" },
          { id: "bd5", source: "arb", target: "retailDex" },
        ],
      },
    },
  ],
};

const SCENARIOS = [
  {
    id: "listing",
    title: "1. 상장 심사 리스크 평가",
    summary:
      "신규 토큰의 네트워크 구조를 사전에 평가하여 상장 여부를 판단합니다.",
    checks: [
      "Density, Reciprocity, Assortativity를 점검해 Rug Pull·Wash Trade 패턴 탐색",
      "위험 점수 7.5 이상이면 상장 보류 및 실사 권고",
    ],
    badge: "TOKENS BEFORE LISTING",
  },
  {
    id: "monitor",
    title: "2. 실시간 이상거래 감지",
    summary:
      "팬아웃 급증, 네트워크 축소 등 이상 징후를 6시간 단위로 모니터링합니다.",
    checks: [
      "Fan-out Δ, Density 감소, Clustering 급락을 조합해 경보 발생",
      "경보시 대시보드 및 담당자 알림 → STR 초안 자동 작성",
    ],
    badge: "LIVE ALERTS",
  },
  {
    id: "investigation",
    title: "3. 조사/추적",
    summary: "허브 노드와 커뮤니티 구조를 분석해 위험 주소를 확장 추적합니다.",
    checks: [
      "Betweenness, Out-degree, Community Risk 기반 허브 식별",
      "KYC/거래내역과 조인하여 STR 보고 및 조치",
    ],
    badge: "FORENSIC",
  },
];

const formatTs = (ts) => {
  try {
    return new Date(ts * 1000).toLocaleString();
  } catch (error) {
    return "-";
  }
};

const tier = (score) => {
  if (score >= 7.5)
    return {
      label: "HIGH",
      color: "background:rgba(248,113,113,0.18); color:#b91c1c",
    };
  if (score >= 4.5)
    return {
      label: "MED",
      color: "background:rgba(251,191,36,0.2); color:#b45309",
    };
  return {
    label: "LOW",
    color: "background:rgba(34,197,94,0.18); color:#15803d",
  };
};

const Stat = ({ label, value }) => (
  <div
    style={{
      padding: "12px",
      borderRadius: "16px",
      border: "1px solid rgba(148,163,184,0.3)",
      background: "white",
    }}
  >
    <div style={{ fontSize: "11px", color: "#64748b" }}>{label}</div>
    <div style={{ fontWeight: 600, marginTop: "4px" }}>{value}</div>
  </div>
);

const Chip = ({ children, style }) => (
  <span className="chip" style={style}>
    {children}
  </span>
);

const GraphView = ({ graphData }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.innerHTML = "";

    if (!graphData || !graphData.nodes || !graphData.nodes.length) return;

    const GraphClass =
      window.graphology?.Graph || window.graphology?.default?.Graph;
    if (!GraphClass) return;

    const SigmaCtor = window.sigma?.Sigma || window.Sigma || window.sigma;
    if (!SigmaCtor) return;

    const graph = new GraphClass();
    graphData.nodes.forEach((node) => {
      if (!graph.hasNode(node.id)) {
        graph.addNode(node.id, node);
      }
    });
    graphData.edges.forEach((edge) => {
      if (!graph.hasEdge(edge.source, edge.target)) {
        graph.addEdge(edge.source, edge.target, edge);
      }
    });

    const renderer = new SigmaCtor(graph, containerRef.current, {
      minCameraRatio: 0.5,
      maxCameraRatio: 1.5,
    });

    return () => renderer.kill();
  }, [graphData]);

  return (
    <div
      ref={containerRef}
      style={{
        height: "220px",
        borderRadius: "16px",
        border: "1px solid rgba(148,163,184,0.3)",
        marginTop: "16px",
      }}
    />
  );
};

const Sidebar = ({ chains, currentChain, onSelect }) => (
  <aside
    style={{
      width: "240px",
      background: "linear-gradient(180deg, #1e1b4b 0%, #312e81 80%)",
      color: "white",
      padding: "32px 24px",
      display: "flex",
      flexDirection: "column",
      gap: "32px",
      boxShadow: "0 10px 40px rgba(15,23,42,0.25)",
    }}
  >
    <div>
      <div style={{ fontSize: "11px", letterSpacing: "0.12em", opacity: 0.7 }}>
        TRACE-X
      </div>
      <h2 style={{ margin: "8px 0 0", fontSize: "22px", fontWeight: 700 }}>
        AML Command
      </h2>
      <p style={{ margin: "4px 0 0", fontSize: "12px", opacity: 0.7 }}>
        블록체인 인텔리전스 & 리스크 대시보드
      </p>
    </div>

    <nav style={{ display: "grid", gap: "10px" }}>
      {[
        {
          label: "대시보드",
          action: () => window.scrollTo({ top: 0, behavior: "smooth" }),
        },
        {
          label: "오늘 감지",
          action: () =>
            document
              .getElementById("alerts-today")
              ?.scrollIntoView({ behavior: "smooth", block: "start" }),
        },
        {
          label: "수동 탐지",
          action: () =>
            document
              .getElementById("manual-investigation")
              ?.scrollIntoView({ behavior: "smooth", block: "start" }),
        },
      ].map((item, idx) => (
        <button
          key={item.label}
          onClick={item.action}
          style={{
            all: "unset",
            padding: "10px 14px",
            borderRadius: "12px",
            fontSize: "13px",
            fontWeight: idx === 0 ? 600 : 500,
            background: idx === 0 ? "rgba(255,255,255,0.12)" : "transparent",
            cursor: "pointer",
          }}
        >
          {item.label}
        </button>
      ))}
    </nav>

    <div
      style={{
        padding: "16px",
        borderRadius: "16px",
        background: "rgba(15, 23, 42, 0.35)",
        display: "grid",
        gap: "10px",
        fontSize: "12px",
      }}
    >
      <span style={{ opacity: 0.7 }}>체인 선택</span>
      <div style={{ display: "grid", gap: "8px" }}>
        {chains.map((c) => (
          <button
            key={c}
            onClick={() => onSelect(c)}
            style={{
              all: "unset",
              padding: "8px 12px",
              borderRadius: "12px",
              background:
                currentChain === c ? "rgba(255,255,255,0.22)" : "transparent",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              cursor: "pointer",
            }}
          >
            <span style={{ fontWeight: 600 }}>{c}</span>
            {currentChain === c && (
              <span
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "999px",
                  background: "#22d3ee",
                  display: "inline-block",
                }}
              />
            )}
          </button>
        ))}
      </div>
    </div>
  </aside>
);

const SummaryCard = ({ title, value, delta, deltaLabel, tone = "default" }) => {
  const toneMap = {
    default: {
      bg: "linear-gradient(135deg, rgba(255,255,255,0.85), rgba(241,245,249,0.9))",
      border: "rgba(148,163,184,0.35)",
      color: "#0f172a",
    },
    danger: {
      bg: "linear-gradient(135deg, rgba(248,113,113,0.18), rgba(248,113,113,0.08))",
      border: "rgba(248,113,113,0.45)",
      color: "#b91c1c",
    },
    warning: {
      bg: "linear-gradient(135deg, rgba(251,191,36,0.18), rgba(251,191,36,0.08))",
      border: "rgba(251,191,36,0.45)",
      color: "#b45309",
    },
  };
  const palette = toneMap[tone] || toneMap.default;

  return (
    <div
      style={{
        padding: "18px",
        borderRadius: "20px",
        border: `1px solid ${palette.border}`,
        background: palette.bg,
        display: "grid",
        gap: "6px",
        boxShadow: "0 18px 35px rgba(15,23,42,0.05)",
      }}
    >
      <span style={{ fontSize: "12px", color: "rgba(15,23,42,0.55)" }}>
        {title}
      </span>
      <div style={{ fontSize: "26px", fontWeight: 700, color: palette.color }}>
        {value}
      </div>
      {delta !== undefined && (
        <span style={{ fontSize: "12px", color: palette.color }}>
          {delta > 0 ? "▲" : "▼"} {Math.abs(delta).toFixed(1)}% · {deltaLabel}
        </span>
      )}
    </div>
  );
};

const DonutChart = ({ distribution }) => {
  const total = distribution.reduce((acc, item) => acc + item.value, 0) || 1;
  let cumulative = 0;
  const gradientStops = distribution
    .map((item) => {
      const start = (cumulative / total) * 360;
      cumulative += item.value;
      const end = (cumulative / total) * 360;
      return `${item.color} ${start}deg ${end}deg`;
    })
    .join(", ");

  return (
    <div style={{ display: "flex", gap: "18px", alignItems: "center" }}>
      <div
        style={{
          width: "150px",
          height: "150px",
          borderRadius: "999px",
          background: `conic-gradient(${gradientStops})`,
          position: "relative",
          boxShadow: "0 20px 40px rgba(15,23,42,0.08)",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: "22px",
            left: "22px",
            right: "22px",
            bottom: "22px",
            background: "white",
            borderRadius: "999px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "13px",
            color: "#0f172a",
            boxShadow: "inset 0 0 15px rgba(15,23,42,0.05)",
          }}
        >
          <strong style={{ fontSize: "22px" }}>
            {distribution[0]?.value ?? 0}
          </strong>
          <span style={{ fontSize: "11px", color: "#64748b" }}>고위험</span>
        </div>
      </div>
      <div style={{ display: "grid", gap: "8px", fontSize: "12px" }}>
        {distribution.map((item) => (
          <div
            key={item.label}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "12px",
            }}
          >
            <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span
                style={{
                  width: "10px",
                  height: "10px",
                  borderRadius: "2px",
                  background: item.color,
                }}
              />
              {item.label}
            </span>
            <span style={{ fontWeight: 600 }}>{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const RiskList = ({ items }) => (
  <div
    style={{
      background: "white",
      borderRadius: "20px",
      border: "1px solid rgba(148,163,184,0.35)",
      padding: "18px",
      display: "grid",
      gap: "12px",
      boxShadow: "0 20px 45px rgba(15,23,42,0.08)",
    }}
  >
    <div style={{ display: "flex", justifyContent: "space-between" }}>
      <h3 style={{ margin: 0, fontSize: "16px", fontWeight: 600 }}>
        오늘 감지된 위험 주소
      </h3>
      <span style={{ fontSize: "12px", color: "#6366f1" }}>자세히 보기</span>
    </div>
    <div style={{ display: "grid", gap: "10px" }}>
      {items.map((item, idx) => (
        <div
          key={`${item.contract}-${idx}`}
          style={{
            display: "grid",
            gridTemplateColumns: "auto 1fr auto auto",
            alignItems: "center",
            gap: "12px",
            padding: "10px 12px",
            borderRadius: "14px",
            background: "rgba(248,113,113,0.08)",
            border: "1px solid rgba(248,113,113,0.32)",
          }}
        >
          <div
            style={{
              width: "26px",
              height: "26px",
              borderRadius: "12px",
              background: "#ef4444",
              color: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "12px",
              fontWeight: 600,
            }}
          >
            {idx + 1}
          </div>
          <div>
            <div style={{ fontSize: "13px", fontWeight: 600 }}>{item.name}</div>
            <div
              style={{
                fontSize: "12px",
                color: "#475569",
                fontFamily: "monospace",
              }}
            >
              {item.contract}
            </div>
          </div>
          <span style={{ fontSize: "12px", color: "#ef4444", fontWeight: 600 }}>
            Risk {item.riskScore.toFixed(1)}
          </span>
          <span
            style={{
              fontSize: "11px",
              padding: "6px 10px",
              borderRadius: "999px",
              background: "white",
              border: "1px solid rgba(248,113,113,0.3)",
              color: "#ef4444",
              fontWeight: 600,
            }}
          >
            {item.chain.toUpperCase()}
          </span>
        </div>
      ))}
    </div>
  </div>
);

const ScenarioCard = ({ scenario }) => (
  <div
    style={{
      border: "1px solid rgba(148,163,184,0.25)",
      borderRadius: "18px",
      padding: "18px",
      background: "rgba(248,250,252,0.8)",
      flex: "1 1 280px",
      minWidth: "260px",
    }}
  >
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "10px",
      }}
    >
      <span
        style={{
          fontSize: "12px",
          letterSpacing: "0.08em",
          color: "#6366f1",
        }}
      >
        {scenario.badge}
      </span>
      <span style={{ fontSize: "18px" }}>🧭</span>
    </div>
    <h3 style={{ margin: "0 0 8px", fontSize: "18px", fontWeight: 600 }}>
      {scenario.title}
    </h3>
    <p style={{ margin: "0 0 12px", fontSize: "13px", color: "#475569" }}>
      {scenario.summary}
    </p>
    <ul
      style={{
        margin: 0,
        padding: "0 0 0 18px",
        fontSize: "13px",
        color: "#334155",
      }}
    >
      {scenario.checks.map((c) => (
        <li key={c} style={{ marginBottom: "6px" }}>
          {c}
        </li>
      ))}
    </ul>
  </div>
);

const MetricGuide = () => (
  <div
    style={{
      border: "1px solid rgba(148,163,184,0.25)",
      borderRadius: "18px",
      padding: "18px",
      background: "white",
      display: "grid",
      gap: "12px",
      gridTemplateColumns: "repeat(auto-fit,minmax(200px,1fr))",
    }}
  >
    <div>
      <h4 style={{ margin: "0 0 6px", fontSize: "14px", fontWeight: 600 }}>
        핵심 지표 해석
      </h4>
      <p style={{ margin: 0, fontSize: "13px", color: "#475569" }}>
        각 지표가 의미하는 위험 신호를 빠르게 파악할 수 있도록 정리했습니다.
      </p>
    </div>
    <div style={{ fontSize: "13px", color: "#334155" }}>
      <strong>Density ↓</strong>: 토큰 자금이 특정 지갑에 집중되는 경향 (유동성
      유출 위험)
    </div>
    <div style={{ fontSize: "13px", color: "#334155" }}>
      <strong>Reciprocity ≈ 0</strong>: 일방향 거래 위주 → 세탁 경로 혹은 허브
      지갑 가능성
    </div>
    <div style={{ fontSize: "13px", color: "#334155" }}>
      <strong>Assortativity &lt; 0</strong>: 허브-말단 구조 → Rug Pull, Wash
      Trading 가능성
    </div>
    <div style={{ fontSize: "13px", color: "#334155" }}>
      <strong>Betweenness ↑</strong>: 네트워크 흐름을 장악한 허브 지갑으로 추가
      조사 필요
    </div>
  </div>
);

function TraceXDemo() {
  const RULE_MODE = true; // render rule-based address UI only
  const CHAINS = Object.keys(MOCK);
  const [chain, setChain] = useState(CHAINS[0]);
  const [q, setQ] = useState("");
  const [sortKey, setSortKey] = useState("riskScore");
  const [selected, setSelected] = useState(null);

  const chainRows = useMemo(() => MOCK[chain] || [], [chain]);

  const data = useMemo(() => {
    const rows = chainRows.filter(
      (r) =>
        r.contract.toLowerCase().includes(q.toLowerCase()) ||
        (r.name || "").toLowerCase().includes(q.toLowerCase())
    );
    return rows.sort((a, b) => (b[sortKey] ?? 0) - (a[sortKey] ?? 0));
  }, [chainRows, q, sortKey]);

  const summary = useMemo(() => {
    const total = chainRows.length;
    const high = chainRows.filter((r) => r.riskScore >= 7.5).length;
    const warn = chainRows.filter(
      (r) => r.riskScore >= 4.5 && r.riskScore < 7.5
    ).length;
    const anomaly = chainRows.filter((r) => r.anomalyScore >= 0.5).length;
    const avgDensity =
      chainRows.reduce((acc, r) => acc + (r.density ?? 0), 0) /
        Math.max(total, 1) || 0;

    return {
      total,
      high,
      warn,
      anomaly,
      highShare: total ? (high / total) * 100 : 0,
      anomalyShare: total ? (anomaly / total) * 100 : 0,
      avgDensity,
    };
  }, [chainRows]);

  const distribution = useMemo(
    () => [
      { label: "고위험", value: summary.high, color: "#f87171" },
      { label: "경보", value: summary.warn, color: "#fbbf24" },
      {
        label: "저위험",
        value: Math.max(summary.total - summary.high - summary.warn, 0),
        color: "#22c55e",
      },
    ],
    [summary.high, summary.warn, summary.total]
  );

  const riskLeaders = useMemo(
    () =>
      chainRows
        .slice()
        .sort((a, b) => b.riskScore - a.riskScore)
        .slice(0, 5),
    [chainRows]
  );

  const transactionFeed = useMemo(() => {
    const rows = [];
    chainRows.forEach((token) => {
      (token.samples || []).forEach((sample) => {
        rows.push({
          tx: sample.tx,
          ts: sample.ts,
          amount: sample.amt,
          token: token.name,
          contract: token.contract,
          chain: token.chain,
          risk: tier(token.riskScore).label,
        });
      });
    });
    return rows.sort((a, b) => (b.amount ?? 0) - (a.amount ?? 0)).slice(0, 6);
  }, [chainRows]);

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: "linear-gradient(135deg, #ede9fe, #e2e8f0)",
      }}
    >
      <Sidebar chains={CHAINS} currentChain={chain} onSelect={setChain} />
      <main
        style={{
          flex: 1,
          padding: "36px 48px",
          display: "flex",
          flexDirection: "column",
          gap: "28px",
        }}
      >
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "18px",
          }}
        >
          <div>
            <div
              style={{
                fontSize: "12px",
                letterSpacing: "0.16em",
                color: "#6366f1",
                fontWeight: 600,
              }}
            >
              DASHBOARD
            </div>
            <h1
              style={{
                margin: "6px 0 8px",
                fontSize: "30px",
                fontWeight: 700,
                color: "#0f172a",
              }}
            >
              블록체인 AML 인텔리전스 & 리스크 플랫폼
            </h1>
            <p style={{ margin: 0, color: "#475569", fontSize: "13px" }}>
              {chain} 체인에서 감시 중인 토큰 네트워크 리스크와 이상 징후를
              한눈에 파악합니다.
            </p>
          </div>
          <div
            style={{
              background: "rgba(255,255,255,0.6)",
              borderRadius: "16px",
              padding: "14px 18px",
              border: "1px solid rgba(148,163,184,0.35)",
              display: "grid",
              gap: "6px",
              fontSize: "12px",
              color: "#475569",
              minWidth: "180px",
            }}
          >
            <span>업데이트</span>
            <strong style={{ fontSize: "16px", color: "#1e293b" }}>
              {new Date().toLocaleString()}
            </strong>
          </div>
        </header>

        {!RULE_MODE && (
          <section
            style={{
              display: "grid",
              gap: "16px",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            }}
          >
            <SummaryCard
              title="관리 중 토큰"
              value={`${summary.total.toLocaleString()}개`}
              delta={summary.highShare}
              deltaLabel="고위험 비중"
            />
            <SummaryCard
              title="고위험 경보"
              value={`${summary.high.toLocaleString()}건`}
              delta={summary.highShare}
              deltaLabel="체인 대비 비중"
              tone="danger"
            />
            <SummaryCard
              title="조사 진행"
              value={`${summary.anomaly.toLocaleString()}건`}
              delta={summary.anomalyShare}
              deltaLabel="이상 패턴 비중"
              tone="warning"
            />
          </section>
        )}

        {/* Address-based rules panel (reads JSON produced by run_rules.py) */}
        <section
          style={{
            background: "white",
            borderRadius: "24px",
            border: "1px solid rgba(148,163,184,0.3)",
            padding: "22px",
            boxShadow: "0 25px 55px rgba(15,23,42,0.08)",
          }}
          id="manual-investigation"
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "12px",
            }}
          >
            <h2 style={{ margin: 0, fontSize: "18px", fontWeight: 600 }}>
              주소 기반 룰 스코어링
            </h2>
            <span style={{ fontSize: "12px", color: "#6366f1" }}>
              result/tracex_rules_output.json
            </span>
          </div>
          {window.AddressRulesPanel ? (
            React.createElement(window.AddressRulesPanel, {
              jsonPath: "result/tracex_rules_output.json",
            })
          ) : (
            <div style={{ color: "#94a3b8" }}>
              AddressRulesPanel 불러오는 중...
            </div>
          )}
        </section>

        {/* 수동 탐지: 검색/파일 업로드 스타터 */}
        <section
          style={{
            background: "white",
            borderRadius: "24px",
            border: "1px solid rgba(148,163,184,0.3)",
            padding: "22px",
            boxShadow: "0 25px 55px rgba(15,23,42,0.08)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "12px",
            }}
          >
            <h2 style={{ margin: 0, fontSize: "18px", fontWeight: 600 }}>
              수동 탐지
            </h2>
            <span style={{ fontSize: "12px", color: "#6366f1" }}>
              Start a new investigation
            </span>
          </div>
          {window.ManualInvestigation ? (
            React.createElement(window.ManualInvestigation, {
              onSearch: (payload) => {
                if (typeof payload === "string") {
                  alert(`Search: ${payload}`);
                } else {
                  alert(`Loaded file: ${payload.fileName}`);
                }
              },
            })
          ) : (
            <div style={{ color: "#94a3b8" }}>
              ManualInvestigation 불러오는 중...
            </div>
          )}
        </section>

        {!RULE_MODE && (
          <section
            style={{
              background: "white",
              borderRadius: "24px",
              border: "1px solid rgba(148,163,184,0.3)",
              padding: "26px",
              display: "grid",
              gap: "24px",
              boxShadow: "0 30px 60px rgba(15,23,42,0.08)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "12px",
              }}
            >
              <div>
                <h2 style={{ margin: 0, fontSize: "18px", fontWeight: 600 }}>
                  위험도 분석
                </h2>
                <p
                  style={{
                    margin: "4px 0 0",
                    fontSize: "12px",
                    color: "#475569",
                  }}
                >
                  고위험 주소 집중도와 평균 네트워크 밀도를 기반으로 감시 지표를
                  제공합니다.
                </p>
              </div>
              <div
                style={{
                  fontSize: "12px",
                  padding: "8px 14px",
                  borderRadius: "999px",
                  background: "rgba(99,102,241,0.12)",
                  color: "#3730a3",
                  fontWeight: 600,
                }}
              >
                평균 밀도 {summary.avgDensity.toFixed(4)}
              </div>
            </div>
            <DonutChart distribution={distribution} />
          </section>
        )}

        <section
          style={{
            display: "grid",
            gap: "20px",
            gridTemplateColumns: "1fr",
          }}
          id="alerts-today"
        >
          {window.AlertsToday ? (
            React.createElement(window.AlertsToday, {
              jsonPath: "result/alerts_today.json",
            })
          ) : (
            <div />
          )}
        </section>

        {/* Duplicate manual investigation section removed */}

        {!RULE_MODE && (
          <section
            style={{
              display: "grid",
              gap: "16px",
              gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            }}
          >
            {SCENARIOS.map((sc) => (
              <ScenarioCard key={sc.id} scenario={sc} />
            ))}
            <MetricGuide />
          </section>
        )}

        <footer
          style={{
            fontSize: "12px",
            color: "#94a3b8",
            paddingTop: "8px",
            paddingBottom: "24px",
          }}
        >
          Demo data only. Replace MOCK with live API response.
        </footer>
      </main>

      {selected && (
        <div className="drawer">
          <div
            style={{
              width: "520px",
              background: "white",
              padding: "24px",
              overflowY: "auto",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
              }}
            >
              <div>
                <h2
                  style={{
                    margin: 0,
                    fontSize: "22px",
                    fontWeight: 600,
                  }}
                >
                  Address Detail
                </h2>
                <p
                  style={{
                    margin: "4px 0",
                    color: "#64748b",
                    fontSize: "13px",
                  }}
                >
                  {selected.contract} · {selected.chain}
                </p>
              </div>
              <button
                onClick={() => setSelected(null)}
                style={{
                  border: "1px solid rgba(148,163,184,0.4)",
                  borderRadius: "10px",
                  padding: "8px 14px",
                }}
              >
                Close
              </button>
            </div>

            {window.RuleAddressDetail ? (
              React.createElement(window.RuleAddressDetail, {
                jsonPath: "result/address_detail_demo.json",
              })
            ) : (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit,minmax(140px,1fr))",
                  gap: "12px",
                  marginTop: "20px",
                }}
              >
                <Stat
                  label="Risk"
                  value={`${selected.riskScore.toFixed(2)} (${
                    tier(selected.riskScore).label
                  })`}
                />
                <Stat
                  label="Anomaly"
                  value={selected.anomalyScore.toFixed(2)}
                />
                <Stat label="Nodes" value={selected.nodes.toLocaleString()} />
                <Stat label="Edges" value={selected.edges.toLocaleString()} />
                <Stat label="Density" value={selected.density.toFixed(5)} />
                <Stat
                  label="Reciprocity"
                  value={selected.reciprocity.toFixed(3)}
                />
                <Stat
                  label="Clustering"
                  value={selected.clustering.toFixed(3)}
                />
                <Stat
                  label="Assortativity"
                  value={(selected.assortativity ?? 0).toFixed(3)}
                />
                <Stat label="Eff. Diameter" value={selected.effDiameter} />
              </div>
            )}

            {!window.RuleAddressDetail && (
              <div style={{ marginTop: "24px" }}>
                <h3
                  style={{
                    fontSize: "14px",
                    fontWeight: 600,
                    marginBottom: "8px",
                  }}
                >
                  탐지 사유
                </h3>
                <div
                  style={{
                    display: "flex",
                    gap: "8px",
                    flexWrap: "wrap",
                  }}
                >
                  {selected.reasons?.length ? (
                    selected.reasons.map((r) => (
                      <span
                        key={r.key}
                        className="chip"
                        style={{ background: "rgba(148,163,184,0.15)" }}
                      >
                        {r.label}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: "#94a3b8", fontSize: "13px" }}>
                      -
                    </span>
                  )}
                </div>
              </div>
            )}

            {!window.RuleAddressDetail && (
              <div style={{ marginTop: "24px" }}>
                <h3
                  style={{
                    fontSize: "14px",
                    fontWeight: 600,
                    marginBottom: "8px",
                  }}
                >
                  인접 토큰 (Global · Jaccard)
                </h3>
                {selected.neighbors?.length ? (
                  <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                    {selected.neighbors.map((n) => (
                      <li
                        key={n.token}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          border: "1px solid rgba(148,163,184,0.3)",
                          borderRadius: "12px",
                          padding: "10px 14px",
                          marginBottom: "6px",
                        }}
                      >
                        <span
                          style={{
                            fontFamily: "monospace",
                            fontSize: "12px",
                          }}
                        >
                          {n.token}
                        </span>
                        <span style={{ color: "#475569" }}>
                          {(n.jaccard * 100).toFixed(1)}%
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ color: "#94a3b8", fontSize: "13px" }}>
                    관련 토큰 없음
                  </p>
                )}
              </div>
            )}

            {!window.RuleAddressDetail && (
              <div style={{ marginTop: "24px" }}>
                <h3
                  style={{
                    fontSize: "14px",
                    fontWeight: 600,
                    marginBottom: "8px",
                  }}
                >
                  네트워크 미니맵
                </h3>
                {selected.graph ? (
                  <>
                    <GraphView graphData={selected.graph} />
                    <p
                      style={{
                        marginTop: "8px",
                        fontSize: "12px",
                        color: "#475569",
                        lineHeight: 1.5,
                      }}
                    >
                      노드 크기는 out-degree, 색은
                      역할(허브/브릿지/엔드포인트)을 나타냅니다.
                    </p>
                  </>
                ) : (
                  <p style={{ color: "#94a3b8", fontSize: "13px" }}>
                    그래프 데이터가 없습니다.
                  </p>
                )}
              </div>
            )}

            {!window.RuleAddressDetail && (
              <div style={{ marginTop: "24px" }}>
                <h3
                  style={{
                    fontSize: "14px",
                    fontWeight: 600,
                    marginBottom: "8px",
                  }}
                >
                  대표 트랜잭션
                </h3>
                {selected.samples?.length ? (
                  <div
                    style={{
                      border: "1px solid rgba(148,163,184,0.3)",
                      borderRadius: "16px",
                      overflow: "hidden",
                    }}
                  >
                    <table style={{ width: "100%", fontSize: "13px" }}>
                      <thead style={{ background: "rgba(241,245,249,0.7)" }}>
                        <tr>
                          <th style={{ padding: "10px", textAlign: "left" }}>
                            Tx
                          </th>
                          <th style={{ padding: "10px", textAlign: "left" }}>
                            Time
                          </th>
                          <th
                            style={{
                              padding: "10px",
                              textAlign: "right",
                            }}
                          >
                            Amount
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {selected.samples.map((s) => (
                          <tr key={s.tx}>
                            <td
                              style={{
                                padding: "10px",
                                fontFamily: "monospace",
                                fontSize: "12px",
                              }}
                            >
                              {s.tx}
                            </td>
                            <td style={{ padding: "10px" }}>
                              {formatTs(s.ts)}
                            </td>
                            <td
                              style={{
                                padding: "10px",
                                textAlign: "right",
                              }}
                            >
                              {s.amt.toLocaleString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p style={{ color: "#94a3b8", fontSize: "13px" }}>-</p>
                )}
              </div>
            )}

            {!window.RuleAddressDetail && (
              <div style={{ marginTop: "32px" }}>
                <h3
                  style={{
                    fontSize: "14px",
                    fontWeight: 600,
                    marginBottom: "8px",
                  }}
                >
                  STR 보고서 초안
                </h3>
                <div
                  style={{
                    border: "1px solid rgba(148,163,184,0.4)",
                    borderRadius: "16px",
                    background: "rgba(241,245,249,0.6)",
                    padding: "16px",
                    fontSize: "13px",
                    lineHeight: 1.6,
                  }}
                >
                  <p>
                    - 토큰:{" "}
                    <span style={{ fontFamily: "monospace" }}>
                      {selected.contract}
                    </span>
                  </p>
                  <p>
                    - 탐지유형:{" "}
                    {selected.reciprocity < 0.05 && selected.clustering < 0.05
                      ? "Rapid Movement / Rug Pull Susp."
                      : "Anomalous Pattern"}
                  </p>
                  <p>
                    - 근거: reciprocity={selected.reciprocity.toFixed(2)},
                    density={selected.density.toFixed(4)}, clustering=
                    {selected.clustering.toFixed(2)}
                  </p>
                  <p>- 권장조치: 거래 제한 및 KYC 재확인</p>
                  <p
                    style={{
                      marginTop: "8px",
                      color: "#1d4ed8",
                      fontWeight: 500,
                    }}
                  >
                    - 다음 단계: AML 대시보드에서 상위 위험 주소 확인 → STR
                    시스템으로 전송
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function cssObj(str) {
  const obj = {};
  str.split(";").forEach((pair) => {
    const [k, v] = pair.split(":");
    if (k && v) {
      const prop = k.trim().replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      obj[prop] = v.trim();
    }
  });
  return obj;
}

ReactDOM.createRoot(document.getElementById("root")).render(<TraceXDemo />);
