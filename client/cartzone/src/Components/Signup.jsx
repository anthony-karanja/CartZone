import React, { useState } from 'react';

function Signup({ onSignup, switchToLogin }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    if (!name || !email || !password) {
      alert('Please fill in all fields.');
      return;
    }
  
    try {
      const response = await fetch('http://localhost:5555/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password_hash: password, role: 'user' }), // ✅ Add role
      });
  
      const data = await response.json();
  
      if (!response.ok) {
        throw new Error(data.error || 'Signup failed');
      }
  
      alert('Signup successful!');
      onSignup?.(data.data); // use `data.data` since your Flask returns user inside "data" key
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="auth-container">
      <h2 className="auth-title">Sign Up</h2>
      <form className="auth-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Full Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="email"
          placeholder="Email Address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Create Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Sign Up</button>
      </form>
      <p className="switch-auth">
        Already have an account? <span onClick={switchToLogin}>Log in</span>
      </p>
    </div>
  );
}

export default Signup;