import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { CheckCircle, XCircle, ChevronDown, ChevronUp, Clock, AlertTriangle } from "lucide-react";

const PRIORITY_COLOR = {
  HIGH:   { bg: "#2d1a1a", text: "#f87171", dot: "#ef4444" },
  MEDIUM: { bg: "#1e1e10", text: "#facc15", dot: "#eab308" },
  LOW:    { bg: "#0f1e10", text: "#86efac", dot: "#22c55e" },
};

const STATUS_ICON = {
  PENDING:  <Clock size={12} />,
  APPROVED: <CheckCircle size={12} />,
  REJECTED: <XCircle size={12} />,
};

const STATUS_COLOR = {
  PENDING:  "#facc15",
  APPROVED: "#a3e635",
  REJECTED: "#f87171",
};

export default function EmailCard({ email, approve, reject }) {
  const [expanded, setExpanded] = useState(false);

  const priority = (email.priority || "LOW").toUpperCase();
  const pColor = PRIORITY_COLOR[priority] || PRIORITY_COLOR.LOW;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        background: "#111",
        border: "1px solid #1e1e1e",
        borderRadius: 14,
        padding: 18,
        display: "flex",
        flexDirection: "column",
        gap: 12,
        cursor: "pointer",
        transition: "border-color 0.2s",
      }}
      whileHover={{ borderColor: "#2e2e2e" }}
      onClick={() => setExpanded((v) => !v)}
    >
      {/* Header row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3
            style={{
              margin: "0 0 4px",
              fontSize: 14,
              fontWeight: 700,
              color: "#f0f0f0",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {email.subject}
          </h3>
          <p style={{ margin: 0, fontSize: 12, color: "#555" }}>{email.sender}</p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0, marginLeft: 12 }}>
          {/* Priority badge */}
          <span
            style={{
              padding: "3px 9px",
              borderRadius: 20,
              fontSize: 10,
              fontWeight: 700,
              background: pColor.bg,
              color: pColor.text,
              letterSpacing: 0.5,
              display: "flex",
              alignItems: "center",
              gap: 4,
            }}
          >
            <span style={{ width: 5, height: 5, borderRadius: "50%", background: pColor.dot, display: "inline-block" }} />
            {priority}
          </span>

          {/* Status */}
          <span
            style={{
              display: "flex",
              alignItems: "center",
              gap: 4,
              fontSize: 11,
              color: STATUS_COLOR[email.status] || "#888",
            }}
          >
            {STATUS_ICON[email.status]}
            {email.status}
          </span>

          {/* Expand chevron */}
          <span style={{ color: "#444" }}>
            {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </span>
        </div>
      </div>

      {/* Tags row */}
      <div style={{ display: "flex", gap: 6 }}>
        {[email.category, email.intent, email.sentiment].filter(Boolean).map((tag) => (
          <span
            key={tag}
            style={{
              padding: "2px 8px",
              borderRadius: 6,
              background: "#1a1a1a",
              border: "1px solid #252525",
              fontSize: 10,
              color: "#666",
              textTransform: "capitalize",
            }}
          >
            {tag}
          </span>
        ))}
      </div>

      {/* Expandable body */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            style={{ overflow: "hidden" }}
            onClick={(e) => e.stopPropagation()}
          >
            {email.body && (
              <div style={{ marginBottom: 12 }}>
                <p style={{ fontSize: 10, color: "#444", textTransform: "uppercase", letterSpacing: 1, margin: "0 0 6px" }}>
                  Original Email
                </p>
                <p style={{ fontSize: 12, color: "#888", lineHeight: 1.6, margin: 0, background: "#0d0d0d", borderRadius: 8, padding: 12 }}>
                  {email.body}
                </p>
              </div>
            )}

            {email.draft_response && (
              <div style={{ marginBottom: 14 }}>
                <p style={{ fontSize: 10, color: "#a3e635", textTransform: "uppercase", letterSpacing: 1, margin: "0 0 6px" }}>
                  AI Draft Response
                </p>
                <p style={{ fontSize: 12, color: "#aaa", lineHeight: 1.6, margin: 0, background: "#0d1a06", border: "1px solid #1a2e0a", borderRadius: 8, padding: 12 }}>
                  {email.draft_response}
                </p>
              </div>
            )}

            {/* Action buttons */}
            {email.status === "PENDING" && (
              <div style={{ display: "flex", gap: 8 }}>
                <motion.button
                  whileHover={{ scale: 1.04 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => approve(email.id)}
                  style={{
                    flex: 1,
                    padding: "9px 0",
                    borderRadius: 10,
                    border: "none",
                    background: "#a3e635",
                    color: "#000",
                    fontWeight: 700,
                    fontSize: 13,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 6,
                  }}
                >
                  <CheckCircle size={14} /> Approve
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.04 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => reject(email.id)}
                  style={{
                    flex: 1,
                    padding: "9px 0",
                    borderRadius: 10,
                    border: "1px solid #2a2a2a",
                    background: "transparent",
                    color: "#f87171",
                    fontWeight: 700,
                    fontSize: 13,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 6,
                  }}
                >
                  <XCircle size={14} /> Reject
                </motion.button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}