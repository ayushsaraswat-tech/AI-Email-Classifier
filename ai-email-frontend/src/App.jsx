import { useEffect, useState } from "react";
import api from "./api";
import Login from "./Login";

function App() {
  const [emails, setEmails] = useState([]);
  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem("token")
  );

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
    await api.post(`/emails/approve/${id}`);
    fetchEmails();
  };

  const rejectEmail = async (id) => {
    await api.post(`/emails/reject/${id}`);
    fetchEmails();
  };

  const logout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
  };

  if (!isLoggedIn) {
    return <Login onLogin={() => setIsLoggedIn(true)} />;
  }

  const filteredEmails = emails
    .filter((e) => (filter === "ALL" ? true : e.status === filter))
    .filter(
      (e) =>
        e.subject.toLowerCase().includes(search.toLowerCase()) ||
        e.sender.toLowerCase().includes(search.toLowerCase())
    );

  return (
    <div className="flex h-screen bg-slate-950 text-white">
      <div className="w-64 bg-slate-900 p-6 flex flex-col justify-between">
        <div>
          <h2 className="text-xl font-bold mb-8">📬 AI Mail</h2>

          {["ALL", "PENDING", "APPROVED", "REJECTED"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className="block mb-2"
            >
              {f}
            </button>
          ))}
        </div>

        <button onClick={logout}>Logout</button>
      </div>

      <div className="flex-1 p-6">
        <button onClick={fetchEmails} className="mb-4">
          Refresh
        </button>

        {filteredEmails.map((email) => (
          <div key={email.id} className="mb-4 border p-3">
            <h2>{email.subject}</h2>
            <p>{email.sender}</p>

            <button onClick={() => approveEmail(email.id)}>
              Approve
            </button>
            <button onClick={() => rejectEmail(email.id)}>
              Reject
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;