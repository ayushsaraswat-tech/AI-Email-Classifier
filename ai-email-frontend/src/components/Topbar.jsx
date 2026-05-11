import { DownloadCloud, Search, UserCircle } from "lucide-react";

export default function Topbar({ setSearch, openProfile, importEmails, importing }) {
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
          letterSpacing: 0,
          fontFamily: "Georgia, serif",
          margin: 0,
        }}
      >
        AI EMAIL CLASSIFIER
      </h1>

      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
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
            placeholder="Search emails..."
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

        <button
          onClick={importEmails}
          disabled={importing}
          title="Fetch connected inboxes"
          style={{
            width: 38,
            height: 38,
            borderRadius: 10,
            border: "1px solid #222",
            background: importing ? "#1d2a0d" : "#141414",
            color: "#a3e635",
            cursor: importing ? "default" : "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <DownloadCloud size={16} />
        </button>

        <button
          onClick={openProfile}
          title="Profile and email accounts"
          style={{
            width: 38,
            height: 38,
            borderRadius: 10,
            border: "1px solid #222",
            background: "#141414",
            color: "#ccc",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <UserCircle size={17} />
        </button>
      </div>
    </header>
  );
}