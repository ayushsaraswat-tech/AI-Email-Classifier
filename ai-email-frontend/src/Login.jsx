import { useState } from "react";
import api from "./api";

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

 const handleLogin = async () => {
  try {
    const res = await api.post("/auth/login", {
      email,
      password,
    });

    localStorage.setItem("token", res.data.access_token);
    onLogin();
  } catch (err) {
    setError("Invalid credentials");
  }
};

const handleRegister = async () => {
  try {
    await api.post("/auth/register", {
      email,
      password,
    });

    alert("User registered! Now login.");
  } catch (err) {
    console.error(err);

    if (err.response) {
      const detail = err.response.data.detail;

      if (Array.isArray(detail)) {
        alert(detail.map(e => e.msg).join("\n"));
      } else {
        alert(detail);
      }
    } else {
      alert("Server error");
    }
  }
};
  return (
    <div className="flex h-screen items-center justify-center bg-slate-950 text-white">
      <div className="bg-slate-900 p-6 rounded-xl w-80">
        <h2 className="text-xl mb-4">Login</h2>

        {error && <p className="text-red-400 mb-2">{error}</p>}

        <input
          type="email"
          placeholder="Email"
          className="w-full mb-3 p-2 bg-slate-800"
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full mb-3 p-2 bg-slate-800"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 p-2 rounded"
        >
          Login
        </button>
        <button
  onClick={handleRegister}
  className="w-full bg-green-600 p-2 rounded mt-2"
>
  Register
</button>
      </div>
    </div>
  );
}

export default Login;