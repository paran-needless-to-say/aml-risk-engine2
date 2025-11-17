const { useEffect, useState } = React;

function AlertsToday({ jsonPath = "result/alerts_today.json", limit = 5 }) {
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        const res = await fetch(jsonPath, { cache: "no-cache" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled)
          setItems(Array.isArray(data) ? data.slice(0, limit) : []);
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
  }, [jsonPath, limit]);

  if (loading) return <div>Loading alerts…</div>;
  if (error) return <div style={{ color: "#c00" }}>Error: {error}</div>;

  return (
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
        <span style={{ fontSize: "12px", color: "#6366f1" }}>{jsonPath}</span>
      </div>
      <div style={{ display: "grid", gap: "10px" }}>
        {items.map((item, idx) => (
          <div
            key={item.address}
            style={{
              display: "grid",
              gridTemplateColumns: "auto 1fr auto auto auto",
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
              <div style={{ fontSize: "13px", fontWeight: 600 }}>
                {item.address}
              </div>
              <div
                style={{
                  fontSize: "12px",
                  color: "#475569",
                  fontFamily: "monospace",
                }}
              >
                C:{item.C.toFixed(1)} E:{item.E.toFixed(1)} B:
                {item.B.toFixed(1)}
              </div>
            </div>
            <span
              style={{ fontSize: "12px", color: "#ef4444", fontWeight: 600 }}
            >
              Risk {item.score.toFixed(1)}
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
              ADDRESS
            </span>
            <a
              href={`result/address_detail_${item.address}.json`}
              onClick={(e) => {
                // Fallback to demo file if specific detail JSON is missing
                fetch(`result/address_detail_${item.address}.json`, {
                  cache: "no-cache",
                })
                  .then((r) => {
                    if (!r.ok) {
                      e.preventDefault();
                      window.open("result/address_detail_demo.json", "_blank");
                    }
                  })
                  .catch(() => {
                    e.preventDefault();
                    window.open("result/address_detail_demo.json", "_blank");
                  });
              }}
              target="_blank"
              rel="noreferrer"
              style={{
                fontSize: "12px",
                padding: "6px 10px",
                borderRadius: "10px",
                border: "1px solid rgba(99,102,241,0.3)",
                background: "rgba(99,102,241,0.1)",
                color: "#4338ca",
                fontWeight: 600,
                textDecoration: "none",
              }}
              title="Open address detail (falls back to demo if not generated)"
            >
              Detail
            </a>
          </div>
        ))}
        {!items.length && (
          <div style={{ color: "#94a3b8", fontSize: "13px" }}>-</div>
        )}
      </div>
    </div>
  );
}

window.AlertsToday = AlertsToday;
