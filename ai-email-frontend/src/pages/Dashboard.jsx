import { BarChart, Bar, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown } from "lucide-react";

const card = (style = {}) => ({
  background: "#111",
  border: "1px solid #1e1e1e",
  borderRadius: 16,
  padding: 20,
  ...style,
});

function StatCard({ label, value, sub, trend, delay = 0 }) {
  const up = trend >= 0;
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4, ease: "easeOut" }}
      style={card()}
    >
      <p style={{ fontSize: 11, color: "#555", textTransform: "uppercase", letterSpacing: 1, margin: "0 0 10px" }}>
        {label}
      </p>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 14 }}>
        <span style={{ fontSize: 32, fontWeight: 800, color: "#fff", letterSpacing: -1 }}>
          {value}
        </span>
        {sub !== undefined && (
          <span style={{ fontSize: 22, fontWeight: 700, color: "#444", marginBottom: 3 }}>
            {sub}
          </span>
        )}
      </div>
      {trend !== undefined && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 4,
            marginTop: 8,
            fontSize: 12,
            color: up ? "#a3e635" : "#f87171",
          }}
        >
          {up ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
          {Math.abs(trend)}% this week
        </div>
      )}
    </motion.div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload?.length) {
    return (
      <div style={{ background: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: 8, padding: "8px 14px", fontSize: 12, color: "#ccc" }}>
        <p style={{ margin: 0, color: "#a3e635", fontWeight: 700 }}>{payload[0].value}</p>
        <p style={{ margin: 0 }}>{label}</p>
      </div>
    );
  }
  return null;
};

export default function Dashboard({ emails }) {
  const approved = emails.filter((e) => e.status === "APPROVED").length;
  const pending  = emails.filter((e) => e.status === "PENDING").length;
  const rejected = emails.filter((e) => e.status === "REJECTED").length;

  const chartData = [
    { name: "Approved", value: approved },
    { name: "Pending",  value: pending },
    { name: "Rejected", value: rejected },
  ];

  return (
    <section style={{ padding: "24px 28px", display: "grid", gridTemplateColumns: "1fr 1fr 1fr 2fr", gap: 16 }}>
      <StatCard label="Total Emails"  value={emails.length} delay={0} />
      <StatCard label="Approved"      value={approved}      delay={0.05} />
      <StatCard label="Pending"       value={pending}       delay={0.1} />

      {/* Chart card */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.4, ease: "easeOut" }}
        style={card({ gridRow: "1", display: "flex", flexDirection: "column", gap: 8 })}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <p style={{ fontSize: 11, color: "#555", textTransform: "uppercase", letterSpacing: 1, margin: 0 }}>
            Weekly Activity
          </p>
          <span style={{ fontSize: 11, color: "#a3e635" }}>This week ▾</span>
        </div>
        <ResponsiveContainer width="100%" height={80}>
          <BarChart data={chartData} barSize={10}>
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#444" }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "#1e1e1e" }} />
            <Bar dataKey="value" fill="#a3e635" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>
    </section>
  );
}