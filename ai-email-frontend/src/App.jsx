import { useEffect, useState } from "react";
import api from "./api";
import Login from "./Login";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import EmailCard from "./components/EmailCard";
import Dashboard from "./pages/Dashboard";

function App() {
  const [emails, setEmails] = useState([]);
  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("token"));

  const fetchEmails = async () => {
    try {
      const res = await api.get("/emails/all");
      setEmails(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (isLoggedIn) fetchEmails();
  }, [isLoggedIn]);

  const approveEmail = async (id) => {
  try {
    const res = await api.post(`/emails/approve/${id}`);
    console.log("APPROVED:", res.data);
    fetchEmails();
  } catch (err) {
    console.error("APPROVE ERROR:", err.response?.data || err);
    alert("Approve failed");
  }
};

  const rejectEmail = async (id) => {
    await api.post(`/emails/reject/${id}`);
    fetchEmails();
  };

  const logout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
  };

  if (!isLoggedIn) return <Login onLogin={() => setIsLoggedIn(true)} />;

  const filteredEmails = emails
    .filter((e) => filter === "ALL" || e.status === filter)
    .filter(
      (e) =>
        e.subject?.toLowerCase().includes(search.toLowerCase()) ||
        e.sender?.toLowerCase().includes(search.toLowerCase())
    );

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        background: "#0a0a0a",
        color: "#fff",
        fontFamily: "'DM Sans', 'Helvetica Neue', sans-serif",
        overflow: "hidden",
      }}
    >
      <Sidebar filter={filter} setFilter={setFilter} logout={logout} />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <Topbar setSearch={setSearch} />

        <main style={{ flex: 1, overflowY: "auto" }}>
          <Dashboard emails={emails} />

          {/* Section header */}
          <div
            style={{
              padding: "0 28px 14px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div>
              <h2 style={{ margin: 0, fontSize: 14, fontWeight: 700, color: "#fff" }}>
                {filter === "ALL" ? "All Emails" : `${filter.charAt(0) + filter.slice(1).toLowerCase()} Emails`}
              </h2>
              <p style={{ margin: "2px 0 0", fontSize: 12, color: "#444" }}>
                {filteredEmails.length} result{filteredEmails.length !== 1 ? "s" : ""}
              </p>
            </div>
          </div>

          {/* Email grid */}
          <div
            style={{
              padding: "0 28px 28px",
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
              gap: 12,
            }}
          >
            {filteredEmails.length === 0 ? (
              <div
                style={{
                  gridColumn: "1 / -1",
                  textAlign: "center",
                  padding: "60px 0",
                  color: "#333",
                  fontSize: 14,
                }}
              >
                No emails found
              </div>
            ) : (
              filteredEmails.map((email) => (
                <EmailCard
                  key={email.id}
                  email={email}
                  approve={approveEmail}
                  reject={rejectEmail}
                />
              ))
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;