import React from "react";

function Navbar({ user, onLogout }) {
  return (
    <nav className="navbar">
      <h2>My Shop</h2>
      {user ? (
        <button onClick={onLogout}>Logout</button>
      ) : (
        <span>Welcome! Please log in</span>
      )}
    </nav>
  );
}

export default Navbar;
