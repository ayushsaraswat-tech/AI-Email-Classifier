import { useEffect, useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8001/emails";

function App() {
  const [emails, setEmails] = useState([]);
  const [filter, setFilter] = useState("ALL");

  const fetchEmails = async () => {
    try {
      const res = await axios.get(`${API}/all`);
      setEmails(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchEmails();
  }, []);

  const approveEmail = async (id) => {
    await axios.post(`${API}/approve/${id}`);
    fetchEmails();
  };

  const rejectEmail = async (id) => {
    await axios.post(`${API}/reject/${id}`);
    fetchEmails();
  };

  const getPriorityColor = (priority) => {
    if (priority === "High") return "#ef4444";
    if (priority === "Medium") return "#f59e0b";
    return "#22c55e";
  };

  const getStatusColor = (status) => {
    if (status === "PENDING") return "#f59e0b";
    if (status === "APPROVED") return "#22c55e";
    if (status === "REJECTED") return "#ef4444";
    return "#3b82f6";
  };

  return (
    <div
      style={{
        padding: "40px",
        fontFamily: "Inter, Arial",
        background: "#0f172a",
        minHeight: "100vh",
        color: "white",
      }}
    >
      <h1 style={{ fontSize: "32px", marginBottom: "20px" }}>
        📬 AI Email Dashboard
      </h1>

      {/* Refresh Button */}
      <button
        onClick={fetchEmails}
        style={{
          marginBottom: "20px",
          padding: "10px 15px",
          background: "#3b82f6",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
        }}
      >
        🔄 Refresh
      </button>

      {/* Filters */}
      <div style={{ marginBottom: "30px" }}>
        <button onClick={() => setFilter("ALL")}>All</button>
        <button onClick={() => setFilter("PENDING")} style={{ marginLeft: "10px" }}>
          Pending
        </button>
        <button onClick={() => setFilter("APPROVED")} style={{ marginLeft: "10px" }}>
          Approved
        </button>
        <button onClick={() => setFilter("REJECTED")} style={{ marginLeft: "10px" }}>
          Rejected
        </button>
      </div>

      {/* CENTER WRAPPER */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        {emails.length === 0 ? (
          <p>No emails found</p>
        ) : (
          emails
            .filter((email) =>
              filter === "ALL" ? true : email.status === filter
            )
            .map((email) => (
              <div
                key={email.id}
                style={{
                  background: "#1e293b",
                  padding: "20px",
                  marginBottom: "20px",
                  borderRadius: "12px",
                  boxShadow: "0 10px 25px rgba(0,0,0,0.3)",
                  width: "100%",
                  maxWidth: "900px",
                }}
              >
                <h2 style={{ fontSize: "20px" }}>{email.subject}</h2>
                <p style={{ color: "#94a3b8" }}>From: {email.sender}</p>

                {/* Tags */}
                <div style={{ marginTop: "10px" }}>
                  <span
                    style={{
                      background: getPriorityColor(email.priority),
                      padding: "5px 10px",
                      borderRadius: "6px",
                      marginRight: "10px",
                      color: "white",
                    }}
                  >
                    {email.priority}
                  </span>

                  <span
                    style={{
                      background: getStatusColor(email.status),
                      padding: "5px 10px",
                      borderRadius: "6px",
                      color: "white",
                    }}
                  >
                    {email.status}
                  </span>
                </div>

                <p style={{ marginTop: "10px" }}>
                  <b>Category:</b> {email.category}
                </p>
                <p>
                  <b>Intent:</b> {email.intent}
                </p>

                {/* Draft */}
                <div style={{ marginTop: "15px" }}>
                  <b>Draft Response:</b>
                  <pre
                    style={{
                      background: "#0f172a",
                      padding: "12px",
                      borderRadius: "8px",
                      whiteSpace: "pre-wrap",
                      wordWrap: "break-word",
                      overflowWrap: "break-word",
                      maxWidth: "100%",
                      overflowX: "auto",
                    }}
                  >
                    {email.draft_response}
                  </pre>
                </div>

                {/* Buttons */}
                <div style={{ marginTop: "10px" }}>
                  <button
                    onClick={() => approveEmail(email.id)}
                    style={{
                      background: "#22c55e",
                      border: "none",
                      padding: "8px 12px",
                      borderRadius: "6px",
                      color: "white",
                      cursor: "pointer",
                    }}
                  >
                    Approve
                  </button>

                  <button
                    onClick={() => rejectEmail(email.id)}
                    style={{
                      background: "#ef4444",
                      border: "none",
                      padding: "8px 12px",
                      borderRadius: "6px",
                      color: "white",
                      marginLeft: "10px",
                      cursor: "pointer",
                    }}
                  >
                    Reject
                  </button>
                </div>

                {/* AI Explanation */}
                <div style={{ marginTop: "15px" }}>
                  <b>AI Explanation:</b>
                  <pre
                    style={{
                      background: "#020617",
                      padding: "12px",
                      borderRadius: "8px",
                      whiteSpace: "pre-wrap",
                      wordWrap: "break-word",
                      overflowWrap: "break-word",
                      maxWidth: "100%",
                      overflowX: "auto",
                    }}
                  >
                    {email.ai_explanation}
                  </pre>
                </div>
              </div>
            ))
        )}
      </div>
    </div>
  );
}

export default App;