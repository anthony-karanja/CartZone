import React, { useState, useEffect } from "react";
import "./index.css";

import Login from "./Components/Login";
import Signup from "./Components/Signup";
import Cart from "./Components/Cart";
import Checkout from "./Components/Checkout";
import Orders from "./Components/Orders";
import Navbar from "./Components/Navbar";
import Shop from "./Components/Shop";
import Home from "./Components/Home";
import Footer from "./Components/Footer";

function App() {
  const [user, setUser] = useState(null);
  const [cartItems, setCartItems] = useState([]);
  const [showLogin, setShowLogin] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      setUser({ token }); // If you later decode token, you can replace this with real user info
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    setCartItems([]); // optional: clear cart on logout
  };

  const addToCart = (product) => {
    setCartItems((prevItems) => {
      const existing = prevItems.find((item) => item.id === product.id);
      if (existing) {
        return prevItems.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prevItems, { ...product, quantity: 1 }];
    });
  };

  const removeFromCart = (id) => {
    setCartItems((prevItems) => prevItems.filter((item) => item.id !== id));
  };

  const updateQuantity = (id, quantity) => {
    setCartItems((prevItems) =>
      prevItems.map((item) =>
        item.id === id ? { ...item, quantity: quantity } : item
      )
    );
  };

  return (
    <div>
      <Navbar user={user} onLogout={handleLogout} />
      {!user ? (
    showLogin ? (
      <Login onLogin={handleLogin} switchToSignup={() => setShowLogin(false)} />
    ) : (
      <Signup switchToLogin={() => setShowLogin(true)} />
    )
  ) : (
        <>
          <Home />
          <Shop addToCart={addToCart} />
          <Cart
            cartItems={cartItems}
            removeFromCart={removeFromCart}
            updateQuantity={updateQuantity}
          />
          <Checkout cartItems={cartItems} />
          <Orders />
          <Footer />
        </>
      )}
    </div>
  );
}

export default App;
