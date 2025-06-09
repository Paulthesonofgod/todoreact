// src/App.jsx
import React, { useState, useEffect } from 'react';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';
import TodoPage from './TodoPage';

const App = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setLoggedIn(false);
  };

  if (loggedIn) return <TodoPage onLogout={handleLogout} />;

  return showRegister ? (
    <>
      <RegisterPage onRegister={() => setShowRegister(false)} />
      <p className="text-center mt-4">
        Already have an account?{' '}
        <button onClick={() => setShowRegister(false)} className="text-blue-600 underline">
          Login
        </button>
      </p>
    </>
  ) : (
    <>
      <LoginPage onLogin={() => setLoggedIn(true)} />
      <p className="text-center mt-4">
        Don't have an account?{' '}
        <button onClick={() => setShowRegister(true)} className="text-green-600 underline">
          Register
        </button>
      </p>
    </>
  );
};

export default App;
