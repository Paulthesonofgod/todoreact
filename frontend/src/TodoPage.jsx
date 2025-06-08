import React, { useEffect, useState } from "react";
import axios from "axios";

export default function TodoPage({ onLogout }) {
  const [tasks, s] = useState([]);
  const token = localStorage.getItem("token");
  useEffect(() => {
    axios.get("http://localhost:8000/tasks", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => s(r.data))
      .catch(() => onLogout());
  }, []);
  const add = async () => {
    const title = prompt("New task:");
    if (title) {
      const r = await axios.post("http://localhost:8000/tasks", { title }, { headers: { Authorization: `Bearer ${token}` } });
      s([...tasks, r.data]);
    }
  };
  return (
    <div className="p-6">
      <button onClick={onLogout} className="bg-red-500 text-white px-4 py-2 mb-4 rounded">Logout</button>
      <h2 className="text-2xl mb-4">Tasks</h2>
      <button onClick={add} className="mb-4 bg-green-500 text-white px-3 py-1 rounded">Add</button>
      <ul>
        {tasks.map(t => (
          <li key={t.id} className="flex justify-between items-center py-1 border-b">
            <span>{t.title}</span>
            <span>{t.completed ? "✅" : ""}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}