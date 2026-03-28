import { useEffect, useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8001/emails";

function App() {
  const [emails, setEmails] = useState([]);
  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");

  const fetchEmails = async () => {
    const res = await axios.get(`${API}/all`);
    setEmails(res.data);
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

  const filteredEmails = emails
    .filter((e) => (filter === "ALL" ? true : e.status === filter))
    .filter(
      (e) =>
        e.subject.toLowerCase().includes(search.toLowerCase()) ||
        e.sender.toLowerCase().includes(search.toLowerCase())
    );

  const count = (status) =>
    emails.filter((e) => e.status === status).length;

  return (
    <div className="flex h-screen bg-slate-950 text-white">

      {/* Sidebar */}
      <div className="w-64 bg-slate-900 p-6 border-r border-slate-800">
        <h2 className="text-xl font-bold mb-8">📬 AI Mail</h2>

        <div className="space-y-2">
          {["ALL", "PENDING", "APPROVED", "REJECTED"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`w-full text-left px-3 py-2 rounded-lg ${
                filter === f
                  ? "bg-blue-600"
                  : "hover:bg-slate-800"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Main */}
      <div className="flex-1 p-6 overflow-y-auto">

        {/* Top Bar */}
        <div className="flex justify-between items-center mb-6">
          <input
            type="text"
            placeholder="Search emails..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-slate-800 px-4 py-2 rounded-lg w-1/3 outline-none"
          />

          <button
            onClick={fetchEmails}
            className="bg-blue-600 px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Refresh
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-900 p-4 rounded-xl">
            <p className="text-sm text-gray-400">Total</p>
            <h2 className="text-xl font-bold">{emails.length}</h2>
          </div>

          <div className="bg-slate-900 p-4 rounded-xl">
            <p className="text-sm text-gray-400">Pending</p>
            <h2 className="text-xl font-bold text-yellow-400">
              {count("PENDING")}
            </h2>
          </div>

          <div className="bg-slate-900 p-4 rounded-xl">
            <p className="text-sm text-gray-400">Approved</p>
            <h2 className="text-xl font-bold text-green-400">
              {count("APPROVED")}
            </h2>
          </div>

          <div className="bg-slate-900 p-4 rounded-xl">
            <p className="text-sm text-gray-400">Rejected</p>
            <h2 className="text-xl font-bold text-red-400">
              {count("REJECTED")}
            </h2>
          </div>
        </div>

        {/* Emails */}
        <div className="space-y-4">
          {filteredEmails.map((email) => (
            <div
              key={email.id}
              className="bg-slate-900 p-5 rounded-xl shadow hover:scale-[1.01] transition"
            >
              <h2 className="text-lg font-semibold">
                {email.subject}
              </h2>
              <p className="text-sm text-gray-400">
                From: {email.sender}
              </p>

              {/* Tags */}
              <div className="flex gap-2 mt-2">
                <span className="bg-red-500 text-xs px-2 py-1 rounded">
                  {email.priority}
                </span>
                <span className="bg-blue-500 text-xs px-2 py-1 rounded">
                  {email.status}
                </span>
              </div>

              <p className="mt-2 text-sm">
                <b>Category:</b> {email.category}
              </p>
              <p className="text-sm">
                <b>Intent:</b> {email.intent}
              </p>

              {/* Draft */}
              <div className="mt-3">
                <b>Draft Response:</b>
                <pre className="bg-slate-950 p-3 rounded mt-1 text-sm whitespace-pre-wrap break-words max-h-40 overflow-y-auto">
                  {email.draft_response}
                </pre>
              </div>

              {/* Actions */}
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => approveEmail(email.id)}
                  className="bg-green-500 px-3 py-1 rounded hover:bg-green-600"
                >
                  Approve
                </button>

                <button
                  onClick={() => rejectEmail(email.id)}
                  className="bg-red-500 px-3 py-1 rounded hover:bg-red-600"
                >
                  Reject
                </button>
              </div>

              {/* Explanation */}
              <div className="mt-3">
                <b>AI Explanation:</b>
                <pre className="bg-black p-3 rounded mt-1 text-sm whitespace-pre-wrap break-words max-h-32 overflow-y-auto">
                  {email.ai_explanation}
                </pre>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;