import React, { useState } from 'react';

function Login({ onLogin, switchToSignup }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setMessage('');
    
    if (!email || !password) {
      setMessage('Please enter both email and password.');
      return;
    }

    setLoading(true);

    fetch("http://localhost:5555/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })
    })
    .then((res) => {
      if (!res.ok) {
        throw new Error("Login failed. Check your credentials.");
      }
      return res.json(); // ✅ Parse JSON response
    })
      .then((data) => {
        if (data.access_token) {
          localStorage.setItem("access_token", data.access_token); // ✅ Save token
          setMessage("Login successful!");
          onLogin?.(data.user); // if user data is included
        } else {
          throw new Error("Login did not return access_token");
        }
      })
      .catch((err) => {
        setMessage(err.message);
      })
      .finally(() => setLoading(false));
  };

  

  return (
    <div className="auth-container">
      <h2 className="auth-title">Login</h2>
      <form className="auth-form" onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Log In'}
        </button>
      </form>

      {message && <p className="auth-error">{message}</p>}

      <p className="switch-auth">
        Don’t have an account?{' '}
        <span onClick={switchToSignup} style={{ cursor: 'pointer', color: '#007bff' }}>
          Sign up
        </span>
      </p>
    </div>
  );
}

export default Login;