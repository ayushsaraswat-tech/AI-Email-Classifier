import { Search } from "lucide-react";

export default function Topbar({ setSearch }) {
  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 28px",
        height: 64,
        borderBottom: "1px solid #1a1a1a",
        background: "#0a0a0a",
        flexShrink: 0,
      }}
    >
      <h1
        style={{
          fontSize: 17,
          fontWeight: 700,
          color: "#fff",
          letterSpacing: -0.5,
          fontFamily: "Georgia, serif",
          margin: 0,
        }}
      >
        AI EMAIL CLASSIFIER
      </h1>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          background: "#141414",
          border: "1px solid #222",
          borderRadius: 8,
          padding: "6px 12px",
        }}
      >
        <Search size={14} color="#444" />
        <input
          placeholder="Search emails…"
          onChange={(e) => setSearch(e.target.value)}
          style={{
            background: "transparent",
            border: "none",
            outline: "none",
            fontSize: 13,
            color: "#ccc",
            width: 160,
          }}
        />
      </div>
    </header>
  );
}