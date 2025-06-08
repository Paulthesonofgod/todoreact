import React, { useState } from "react";
import axios from "axios";

export default function LoginPage({ onLogin }) {
  const [u, setU] = useState(""), [p, setP] = useState(""), [e, setE] = useState("");
  const login = async e1 => { e1.preventDefault();
    try {
      const r = await axios.post("http://localhost:8000/auth/login", { username: u, password: p });
      localStorage.setItem("token", r.data.access_token);
      onLogin();
    } catch {
      setE("Invalid credentials");
    }
  };
  return (
    <div className="flex justify-center items-center h-screen bg-gray-100">
      <form onSubmit={login} className="bg-white p-6 rounded shadow">
        <h2 className="text-2xl mb-4">Login</h2>
        {e && <p className="text-red-500">{e}</p>}
        <input className="border p-2 mb-2 w-full" placeholder="Username" value={u} onChange={e => setU(e.target.value)} />
        <input className="border p-2 mb-4 w-full" type="password" placeholder="Password" value={p} onChange={e => setP(e.target.value)} />
        <button className="bg-blue-500 text-white py-2 w-full rounded">Login</button>
      </form>
    </div>
  );
}