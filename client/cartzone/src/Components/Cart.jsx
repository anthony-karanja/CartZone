import React, { useState, useEffect } from "react";

function Cart() {
  const [items, setItems] = useState([]);

  // Fetch cart items on mount
  useEffect(() => {
    const token = localStorage.getItem("access_token");
  
    fetch("http://localhost:5555/cart", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Unauthorized");
        }
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data)) {
          setItems(data);
        } else {
          setItems([]); // fallback
          console.warn("Cart data is not an array:", data);
        }
      })
      .catch((error) => {
        console.error("Error fetching cart:", error);
        setItems([]); // prevent crash
      });
  }, []);

  const handleUpdateQuantity = (itemId, newQuantity) => {
    const token = localStorage.getItem("access_token");
    fetch(`http://localhost:5555/cart/${itemId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ quantity: newQuantity }),
    })
      .then((res) => res.json())
      .then((updatedItem) => {
        setItems((prevItems) =>
          prevItems.map((item) =>
            item.id === updatedItem.id ? updatedItem : item
          )
        );
      });
  };

  const handleRemoveFromCart = (itemId) => {
    const token = localStorage.getItem("access_token");
    fetch(`http://localhost:5555/cart/${itemId}`, {
      method: "DELETE",
      headers: { 
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    }).then(() => {
      setItems((prevItems) => prevItems.filter((item) => item.id !== itemId));
    });
  };

  const total = Array.isArray(items)
  ? items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  : 0;

  return (
    <div id="cart" className="cart">
      <h2 className="section-title">Your Cart</h2>
      {items.length === 0 ? (
        <p className="empty-cart">Your cart is empty.</p>
      ) : (
        <div>
          {items.map((item) => (
            <div key={item.id} className="cart-item">
              <img src={item.image} alt={item.name} className="cart-img" />
              <div className="cart-details">
                <h3>{item.name}</h3>
                <p>KES {item.price.toLocaleString()}</p>
                <input
                  type="number"
                  min="1"
                  value={item.quantity}
                  onChange={(e) =>
                    handleUpdateQuantity(item.id, parseInt(e.target.value))
                  }
                />
                <button onClick={() => handleRemoveFromCart(item.id)}>
                  Remove
                </button>
              </div>
            </div>
          ))}
          <h3 className="cart-total">Total: KES {total.toLocaleString()}</h3>
        </div>
      )}
    </div>
  );
}

export default Cart;
