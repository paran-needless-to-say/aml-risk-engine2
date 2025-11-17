const { useEffect, useState } = React;

/**
 * Minimal address rules panel (non-breaking).
 * Usage:
 *  <AddressRulesPanel jsonPath="/result/tracex_rules_output.json" />
 * or pass data directly:
 *  <AddressRulesPanel data={resultsArray} />
 */
function AddressRulesPanel({ jsonPath, data }) {
  const [results, setResults] = useState(Array.isArray(data) ? data : null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(!data && !!jsonPath);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!jsonPath || data) return;
      try {
        setLoading(true);
        const res = await fetch(jsonPath, { cache: "no-cache" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        if (!cancelled) setResults(json);
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
  }, [jsonPath, data]);

  if (loading) return <div>Loading address risk…</div>;
  if (error) return <div style={{ color: "#c00" }}>Error: {error}</div>;
  if (!results || results.length === 0) return <div>No results.</div>;

  const aggregate = results.reduce(
    (acc, r) => {
      acc.total += r.total_risk_score || 0;
      acc.C += r.compliance_score || 0;
      acc.E += r.exposure_score || 0;
      acc.B += r.behavior_score || 0;
      return acc;
    },
    { total: 0, C: 0, E: 0, B: 0 }
  );

  return (
    <div style={{ border: "1px solid #eee", borderRadius: 8, padding: 16 }}>
      <h3 style={{ marginTop: 0 }}>Address Risk (Rule-based)</h3>
      <div style={{ display: "flex", gap: 16, marginBottom: 12 }}>
        <ScoreCard label="Total" value={aggregate.total.toFixed(1)} />
        <ScoreCard label="Compliance (C)" value={aggregate.C.toFixed(1)} />
        <ScoreCard label="Exposure (E)" value={aggregate.E.toFixed(1)} />
        <ScoreCard label="Behavior (B)" value={aggregate.B.toFixed(1)} />
      </div>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <Th>Tx Hash</Th>
            <Th>Rules</Th>
            <Th>Total</Th>
            <Th>C</Th>
            <Th>E</Th>
            <Th>B</Th>
          </tr>
        </thead>
        <tbody>
          {results.map((r, idx) => (
            <tr
              key={r.tx_hash || idx}
              style={{ borderTop: "1px solid #f0f0f0" }}
            >
              <Td style={{ fontFamily: "monospace" }}>{r.tx_hash || "-"}</Td>
              <Td>
                {Array.isArray(r.rules_triggered) &&
                r.rules_triggered.length > 0
                  ? r.rules_triggered.map((x) => (
                      <span key={x} style={pillStyle}>
                        {x}
                      </span>
                    ))
                  : "-"}
              </Td>
              <Td>{fmt(r.total_risk_score)}</Td>
              <Td>{fmt(r.compliance_score)}</Td>
              <Td>{fmt(r.exposure_score)}</Td>
              <Td>{fmt(r.behavior_score)}</Td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
        Source: rules/tracex_rules.yaml — Run via run_rules.py
      </div>
    </div>
  );
}

function ScoreCard({ label, value }) {
  return (
    <div
      style={{
        border: "1px solid #eee",
        borderRadius: 8,
        padding: "8px 12px",
        minWidth: 120,
      }}
    >
      <div style={{ fontSize: 12, color: "#666" }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 700 }}>{value}</div>
    </div>
  );
}

const Th = (props) => (
  <th
    {...props}
    style={{
      textAlign: "left",
      padding: "8px 6px",
      fontSize: 12,
      color: "#666",
      fontWeight: 600,
    }}
  />
);

const Td = (props) => (
  <td {...props} style={{ padding: "8px 6px", fontSize: 13 }} />
);

const pillStyle = {
  display: "inline-block",
  background: "#f5f5f5",
  border: "1px solid #eee",
  borderRadius: 999,
  padding: "2px 8px",
  marginRight: 6,
  marginBottom: 4,
  fontSize: 12,
};

function fmt(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return "-";
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(1) : "-";
}

// Expose globally for index.html + Babel environment
window.AddressRulesPanel = AddressRulesPanel;
