import { useState } from "react";
import { LogIn, Mail, ShieldCheck, UserPlus } from "lucide-react";
import { motion } from "framer-motion";
import api from "./api";

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [mode, setMode] = useState("login");

  const handleLogin = async () => {
    setError("");
    try {
      const res = await api.post("/auth/login", {
        email,
        password,
      });

      localStorage.setItem("token", res.data.access_token);
      onLogin();
    } catch {
      setError("Invalid credentials");
    }
  };

  const handleRegister = async () => {
    setError("");
    try {
      await api.post("/auth/register", {
        email,
        password,
      });

      setMode("login");
      setError("Account created. You can sign in now.");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.map((e) => e.msg).join("\n") : detail || "Server error");
    }
  };

  const submit = (event) => {
    event.preventDefault();
    if (mode === "login") {
      handleLogin();
    } else {
      handleRegister();
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0a0a0a",
        color: "#fff",
        fontFamily: "'DM Sans', 'Helvetica Neue', sans-serif",
        display: "grid",
        gridTemplateColumns: "minmax(0, 1fr) minmax(360px, 440px)",
      }}
    >
      <section
        style={{
          padding: 44,
          borderRight: "1px solid #1a1a1a",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          minWidth: 0,
        }}
      >
        <div
          style={{
            width: 38,
            height: 38,
            borderRadius: 10,
            background: "#a3e635",
            color: "#000",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: "Georgia, serif",
            fontWeight: 900,
          }}
        >
          AI
        </div>

        <div style={{ maxWidth: 620 }}>
          <p style={{ color: "#555", fontSize: 12, textTransform: "uppercase", letterSpacing: 1, marginBottom: 14 }}>
            AI Email Classifier
          </p>
          <h1 style={{ fontSize: 44, lineHeight: 1.05, margin: 0, letterSpacing: 0, fontWeight: 800 }}>
            Review, classify, and approve your inbox from one focused workspace.
          </h1>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12 }}>
          {[
            ["Pending", "Queue ready for review"],
            ["Drafts", "AI replies with signatures"],
            ["Accounts", "Primary and alternate inboxes"],
          ].map(([label, value]) => (
            <div key={label} style={{ background: "#111", border: "1px solid #1e1e1e", borderRadius: 14, padding: 16 }}>
              <p style={{ color: "#555", fontSize: 11, textTransform: "uppercase", letterSpacing: 1, margin: "0 0 8px" }}>
                {label}
              </p>
              <p style={{ color: "#ccc", fontSize: 13, margin: 0 }}>{value}</p>
            </div>
          ))}
        </div>
      </section>

      <main style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: 28 }}>
        <motion.form
          onSubmit={submit}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
          style={{
            width: "100%",
            background: "#111",
            border: "1px solid #1e1e1e",
            borderRadius: 16,
            padding: 24,
            display: "flex",
            flexDirection: "column",
            gap: 14,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
            <div>
              <p style={{ color: "#555", fontSize: 11, textTransform: "uppercase", letterSpacing: 1, margin: "0 0 6px" }}>
                Workspace Access
              </p>
              <h2 style={{ fontSize: 22, margin: 0 }}>{mode === "login" ? "Sign in" : "Create account"}</h2>
            </div>
            <ShieldCheck size={22} color="#a3e635" />
          </div>

          {error && (
            <p style={{ color: error.includes("created") ? "#a3e635" : "#f87171", fontSize: 13, margin: 0, lineHeight: 1.5 }}>
              {error}
            </p>
          )}

          <label style={{ display: "flex", flexDirection: "column", gap: 7, color: "#666", fontSize: 12 }}>
            Email
            <span style={{ display: "flex", alignItems: "center", gap: 8, background: "#0d0d0d", border: "1px solid #252525", borderRadius: 10, padding: "0 12px" }}>
              <Mail size={15} color="#555" />
              <input
                type="email"
                value={email}
                required
                placeholder="you@example.com"
                onChange={(e) => setEmail(e.target.value)}
                style={{ flex: 1, height: 42, background: "transparent", border: 0, outline: 0, color: "#eee", fontSize: 14 }}
              />
            </span>
          </label>

          <label style={{ display: "flex", flexDirection: "column", gap: 7, color: "#666", fontSize: 12 }}>
            Password
            <input
              type="password"
              value={password}
              required
              placeholder="Password"
              onChange={(e) => setPassword(e.target.value)}
              style={{ height: 42, background: "#0d0d0d", border: "1px solid #252525", borderRadius: 10, outline: 0, color: "#eee", fontSize: 14, padding: "0 12px" }}
            />
          </label>

          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            type="submit"
            style={{
              height: 42,
              border: 0,
              borderRadius: 10,
              background: "#a3e635",
              color: "#000",
              fontWeight: 800,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 8,
            }}
          >
            {mode === "login" ? <LogIn size={16} /> : <UserPlus size={16} />}
            {mode === "login" ? "Sign in" : "Register"}
          </motion.button>

          <button
            type="button"
            onClick={() => {
              setError("");
              setMode(mode === "login" ? "register" : "login");
            }}
            style={{ background: "transparent", border: 0, color: "#777", cursor: "pointer", fontSize: 13 }}
          >
            {mode === "login" ? "Need an account? Register" : "Already have an account? Sign in"}
          </button>
        </motion.form>
      </main>
    </div>
  );
}

export default Login;
