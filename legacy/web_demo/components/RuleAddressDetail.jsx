const { useEffect, useState } = React;

function RuleAddressDetail({ jsonPath = "result/address_detail_demo.json" }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        const res = await fetch(jsonPath, { cache: "no-cache" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        if (!cancelled) setData(json);
      } catch (e) {
        if (!cancelled) setError(String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [jsonPath]);

  if (loading) return <div>Loading address detail…</div>;
  if (error) return <div style={{ color: "#c00" }}>Error: {error}</div>;
  if (!data) return <div>No data.</div>;

  const { address, chain, analyzed_at, scores, rules, evidence, tx_recent } =
    data;

  return (
    <div style={{ display: "grid", gap: "16px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "16px",
          flexWrap: "wrap",
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontSize: "22px", fontWeight: 600 }}>
            Address Detail
          </h2>
          <p
            style={{
              margin: "4px 0",
              color: "#64748b",
              fontSize: "13px",
              fontFamily: "monospace",
            }}
          >
            {address} · {chain} · {analyzed_at}
          </p>
        </div>
      </div>

      {/* Score cards */}
      <div
        style={{
          display: "grid",
          gap: "12px",
          gridTemplateColumns: "repeat(auto-fit,minmax(140px,1fr))",
        }}
      >
        <Card label="Risk (Total)">{fmt(scores?.total)}</Card>
        <Card label="Compliance (C)">{fmt(scores?.C)}</Card>
        <Card label="Exposure (E)">{fmt(scores?.E)}</Card>
        <Card label="Behavior (B)">{fmt(scores?.B)}</Card>
      </div>

      {/* Evidence badges */}
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        {evidence?.sdn && <Chip>SDN</Chip>}
        {Number.isFinite(evidence?.hop) && <Chip>HOP≤{evidence.hop}</Chip>}
        {evidence?.mixer && <Chip>MIXER</Chip>}
        {evidence?.cex_internal && <Chip>CEX_INTERNAL</Chip>}
      </div>

      {/* Rules list */}
      <div
        style={{
          border: "1px solid rgba(148,163,184,0.3)",
          borderRadius: "16px",
          overflow: "hidden",
          background: "white",
        }}
      >
        <table style={{ width: "100%", fontSize: "13px" }}>
          <thead style={{ background: "rgba(241,245,249,0.7)" }}>
            <tr>
              <th style={{ padding: "10px", textAlign: "left" }}>Rule</th>
              <th style={{ padding: "10px", textAlign: "left" }}>Severity</th>
              <th style={{ padding: "10px", textAlign: "right" }}>Score</th>
              <th style={{ padding: "10px", textAlign: "left" }}>Reason</th>
            </tr>
          </thead>
          <tbody>
            {(rules || []).map((r) => (
              <tr key={r.id}>
                <td style={{ padding: "10px" }}>
                  <Chip neutral>{r.id}</Chip> {r.name}
                </td>
                <td style={{ padding: "10px" }}>
                  <Severity sev={r.severity} />
                </td>
                <td style={{ padding: "10px", textAlign: "right" }}>
                  {fmt(r.score)}
                </td>
                <td style={{ padding: "10px" }}>{r.reason || "-"}</td>
              </tr>
            ))}
            {!rules?.length && (
              <tr>
                <td colSpan={4} style={{ padding: "10px", color: "#94a3b8" }}>
                  No rules triggered.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Recent transactions */}
      <div>
        <h3
          style={{
            fontSize: "14px",
            fontWeight: 600,
            marginBottom: "8px",
          }}
        >
          최근 트랜잭션
        </h3>
        <div
          style={{
            border: "1px solid rgba(148,163,184,0.3)",
            borderRadius: "16px",
            overflow: "hidden",
            background: "white",
          }}
        >
          <table style={{ width: "100%", fontSize: "13px" }}>
            <thead style={{ background: "rgba(241,245,249,0.7)" }}>
              <tr>
                <th style={{ padding: "10px", textAlign: "left" }}>Tx</th>
                <th style={{ padding: "10px", textAlign: "left" }}>Time</th>
                <th style={{ padding: "10px", textAlign: "right" }}>USD</th>
                <th style={{ padding: "10px", textAlign: "left" }}>Dir</th>
                <th style={{ padding: "10px", textAlign: "left" }}>Rules</th>
              </tr>
            </thead>
            <tbody>
              {(tx_recent || []).map((t) => (
                <tr key={t.tx_hash}>
                  <td
                    style={{
                      padding: "10px",
                      fontFamily: "monospace",
                      fontSize: "12px",
                    }}
                  >
                    {t.tx_hash}
                  </td>
                  <td style={{ padding: "10px" }}>{formatTs(t.ts)}</td>
                  <td style={{ padding: "10px", textAlign: "right" }}>
                    {Number(t.usd_value || 0).toLocaleString()}
                  </td>
                  <td style={{ padding: "10px" }}>{t.dir || "-"}</td>
                  <td style={{ padding: "10px" }}>
                    {(t.rules || []).map((id) => (
                      <Chip key={id} neutral>
                        {id}
                      </Chip>
                    ))}
                  </td>
                </tr>
              ))}
              {!tx_recent?.length && (
                <tr>
                  <td
                    colSpan={5}
                    style={{ padding: "10px", color: "#94a3b8", textAlign: "center" }}
                  >
                    -
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Card({ label, children }) {
  return (
    <div
      style={{
        border: "1px solid rgba(148,163,184,0.35)",
        borderRadius: "16px",
        background: "linear-gradient(135deg, rgba(255,255,255,0.85), rgba(241,245,249,0.9))",
        padding: "14px",
      }}
    >
      <div style={{ fontSize: "12px", color: "#64748b" }}>{label}</div>
      <div style={{ fontSize: "22px", fontWeight: 700 }}>{children}</div>
    </div>
  );
}

function Chip({ children, neutral }) {
  return (
    <span
      className="chip"
      style={{
        background: neutral ? "rgba(148,163,184,0.12)" : "rgba(59,130,246,0.08)",
        border: "1px solid rgba(148,163,184,0.3)",
        color: "#1f2937",
      }}
    >
      {children}
    </span>
  );
}

function Severity({ sev }) {
  const map = {
    HIGH: { bg: "rgba(248,113,113,0.14)", color: "#b91c1c" },
    MEDIUM: { bg: "rgba(251,191,36,0.14)", color: "#b45309" },
    LOW: { bg: "rgba(34,197,94,0.14)", color: "#15803d" },
  };
  const style = map[sev] || map.LOW;
  return (
    <span
      style={{
        padding: "4px 10px",
        borderRadius: "999px",
        background: style.bg,
        color: style.color,
        fontWeight: 600,
        fontSize: "11px",
      }}
    >
      {sev}
    </span>
  );
}

function fmt(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return "-";
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(1) : "-";
}

function formatTs(ts) {
  try {
    return new Date(ts * 1000).toLocaleString();
  } catch (e) {
    return "-";
  }
}

window.RuleAddressDetail = RuleAddressDetail;


