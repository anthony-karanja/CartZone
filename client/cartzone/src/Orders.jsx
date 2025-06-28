import React, { useEffect, useState } from "react";

function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://localhost:5000/orders")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch orders.");
        return res.json();
      })
      .then((data) => {
        setOrders(data);
        setMessage("");
      })
      .catch((err) => {
        setMessage("Could not load your orders. Please try again.");
        console.error(err);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="orders">
      <h2 className="section-title">My Orders</h2>

      {loading ? (
        <p>Loading orders...</p>
      ) : message ? (
        <p className="orders-error">{message}</p>
      ) : orders.length === 0 ? (
        <p>You have not placed any orders yet.</p>
      ) : (
        <ul className="order-list">
          {orders.map((order) => (
            <li key={order.id} className="order-card">
              <div>
                <strong>Order ID:</strong> {order.id}
              </div>
              <div>
                <strong>Date:</strong> {order.date}
              </div>
              <div>
                <strong>Status:</strong> {order.status}
              </div>
              <div>
                <strong>Total:</strong> KES {order.total.toLocaleString()}
              </div>
              <div className="ordered-items">
                {order.items.map((item, index) => (
                  <div key={index}>
                    {item.name} x{item.quantity}
                  </div>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Orders;