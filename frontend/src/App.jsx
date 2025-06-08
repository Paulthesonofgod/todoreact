import React, { useState } from "react";
import LoginPage from "./LoginPage";
import TodoPage from "./TodoPage";
import "./index.css";

function App() {
  const [inited, setInit] = useState(!!localStorage.getItem("token"));
  const logout = () => { localStorage.removeItem("token"); setInit(false); };
  const loginOk = () => setInit(true);
  return inited ? <TodoPage onLogout={logout} /> : <LoginPage onLogin={loginOk} />;
}

export default App;