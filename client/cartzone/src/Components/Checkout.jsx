import React, { useState } from "react";

function Checkout({ cartItems = [], onOrderSuccess }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const total = cartItems.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  const handlePlaceOrder = async () => {
    setLoading(true);
    setMessage("");

    const token = localStorage.getItem("access_token");

    if (!token) {
      setMessage("You must be logged in to place an order.");
      setLoading(false);
      return;
    }

    const orderPayload = {
      total_amount: total,
      order_items: cartItems.map((item) => ({
        product_id: item.id,
        quantity: item.quantity,
        price_at_purchase: item.price,
      })),
    };

    try {
      const response = await fetch("http://localhost:5555/orders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(orderPayload),
      });

      if (!response.ok) {
        throw new Error("Failed to place order");
      }

      await response.json();
      setMessage("✅ Order placed successfully!");
      onOrderSuccess?.(); // Clear cart if callback provided
    } catch (error) {
      console.error("Order error:", error);
      setMessage("❌ Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkout">
      <h2 className="section-title">Checkout</h2>

      {cartItems.length === 0 ? (
        <p>Your cart is empty. Add items before checking out.</p>
      ) : (
        <div>
          <ul className="checkout-list">
            {cartItems.map((item) => (
              <li key={item.id} className="checkout-item">
                <span>{item.name}</span>
                <span>x{item.quantity}</span>
                <span>
                  KES {(item.price * item.quantity).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>

          <h3 className="checkout-total">
            Total: KES {total.toLocaleString()}
          </h3>

          <button
            onClick={handlePlaceOrder}
            className="place-order-btn"
            disabled={loading}
          >
            {loading ? "Placing Order..." : "Place Order"}
          </button>

          {message && <p className="checkout-message">{message}</p>}
        </div>
      )}
    </div>
  );
}

export default Checkout;
