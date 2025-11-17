const { useState } = React;

function ManualInvestigation({ onSearch }) {
  const [query, setQuery] = useState("");
  const [dragOver, setDragOver] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    onSearch && onSearch(q);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer?.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      // Expecting .gs or json graph file; just emit the text for demo
      onSearch && onSearch({ fileName: file.name, content: reader.result });
    };
    reader.readAsText(file);
  };

  const boxStyle = {
    border: "2px dashed #cbd5e1",
    borderRadius: "14px",
    padding: "22px",
    textAlign: "center",
    background: dragOver ? "rgba(99,102,241,0.06)" : "white",
    transition: "background 120ms ease",
    cursor: "pointer",
  };

  return (
    <div
      className="card"
      style={{
        padding: "24px",
        display: "grid",
        gap: "16px",
        background: "white",
      }}
    >
      <h3 style={{ margin: 0, fontSize: "18px", fontWeight: 700 }}>
        Start a new investigation
      </h3>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: "8px" }}>
        <div
          style={{
            position: "relative",
            flex: 1,
          }}
        >
          <span
            style={{
              position: "absolute",
              left: 12,
              top: 10,
              color: "#94a3b8",
            }}
          >
            🔎
          </span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Address, transaction"
            style={{
              width: "100%",
              padding: "10px 12px 10px 34px",
              borderRadius: "12px",
              border: "1px solid #cbd5e1",
              fontSize: "14px",
              outline: "none",
            }}
          />
        </div>
        <button
          type="submit"
          style={{
            padding: "10px 14px",
            borderRadius: "12px",
            border: "1px solid rgba(99,102,241,0.4)",
            background: "rgba(99,102,241,0.1)",
            color: "#4338ca",
            fontWeight: 700,
          }}
        >
          Search
        </button>
      </form>

      <div style={{ fontSize: "12px", color: "#64748b" }}>
        Try an example:{" "}
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setQuery("0x1111111111111111111111111111111111111111");
          }}
        >
          address
        </a>{" "}
        /{" "}
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setQuery(
              "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            );
          }}
        >
          transaction
        </a>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => {
          const input = document.createElement("input");
          input.type = "file";
          input.accept = ".gs,.json,.txt";
          input.onchange = (ev) => {
            const f = ev.target.files?.[0];
            if (!f) return;
            const reader = new FileReader();
            reader.onload = () =>
              onSearch &&
              onSearch({ fileName: f.name, content: reader.result });
            reader.readAsText(f);
          };
          input.click();
        }}
        style={boxStyle}
      >
        <div style={{ fontSize: "26px" }}>📁</div>
        <div style={{ fontWeight: 600, marginTop: 6 }}>
          Load graph from .gs file
        </div>
        <div style={{ fontSize: "12px", color: "#64748b", marginTop: 2 }}>
          Drag & drop or click to upload
        </div>
      </div>
    </div>
  );
}

// Expose to window for index.html
window.ManualInvestigation = ManualInvestigation;
