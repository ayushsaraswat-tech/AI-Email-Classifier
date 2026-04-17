import { LayoutDashboard, Mail, CheckCircle, XCircle, Clock, LogOut } from "lucide-react";
import { motion } from "framer-motion";

const NAV_ITEMS = [
  { key: "ALL",      icon: LayoutDashboard, label: "All" },
  { key: "PENDING",  icon: Clock,           label: "Pending" },
  { key: "APPROVED", icon: CheckCircle,     label: "Approved" },
  { key: "REJECTED", icon: XCircle,         label: "Rejected" },
];

export default function Sidebar({ filter, setFilter, logout }) {
  return (
    <aside
      style={{
        width: 72,
        minHeight: "100vh",
        background: "#0a0a0a",
        borderRight: "1px solid #1a1a1a",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        paddingTop: 24,
        paddingBottom: 24,
        gap: 0,
      }}
    >
      {/* Logo */}
      <div
        style={{
          width: 38,
          height: 38,
          borderRadius: 10,
          background: "#a3e635",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontWeight: 900,
          fontSize: 18,
          color: "#000",
          marginBottom: 36,
          letterSpacing: -1,
          fontFamily: "Georgia, serif",
        }}
      >
        AI
      </div>

      {/* Nav */}
      <nav style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1 }}>
        {NAV_ITEMS.map(({ key, icon: Icon, label }) => {
          const active = filter === key;
          return (
            <motion.button
              key={key}
              onClick={() => setFilter(key)}
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.95 }}
              title={label}
              style={{
                width: 44,
                height: 44,
                borderRadius: 12,
                border: "none",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: active ? "#a3e635" : "transparent",
                color: active ? "#000" : "#555",
                transition: "background 0.2s, color 0.2s",
                position: "relative",
              }}
            >
              <Icon size={18} strokeWidth={active ? 2.5 : 1.8} />
              {active && (
                <motion.div
                  layoutId="activeIndicator"
                  style={{
                    position: "absolute",
                    right: -13,
                    width: 3,
                    height: 20,
                    borderRadius: 4,
                    background: "#a3e635",
                  }}
                />
              )}
            </motion.button>
          );
        })}
      </nav>

      {/* Bottom actions */}
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <motion.button
          onClick={logout}
          whileHover={{ scale: 1.08 }}
          whileTap={{ scale: 0.95 }}
          title="Logout"
          style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            border: "none",
            background: "#1a1a1a",
            color: "#ef4444",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <LogOut size={16} />
        </motion.button>
      </div>
    </aside>
  );
}