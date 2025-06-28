import React, { useEffect, useState } from "react";

function Shop({ token, user }) {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    price: "",
    stock_quantity: "",
    image_url: "",
  });

  const [products, setProducts] = useState([]);
  const [error, setError] = useState("");

  const isAdmin = user?.role === "admin"; // role check

  // Fetch all products
  useEffect(() => {
    fetch("http://localhost:5000/products")
      .then((r) => r.json())
      .then(setProducts)
      .catch(() => setError("Failed to load products"));
  }, []);

  // Handle input changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isAdmin) {
      setError("Only admins can upload products.");
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/products", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        const data = await res.json();
        alert("Product uploaded!");
        setProducts([...products, data.data]); // Update list
        setFormData({
          name: "",
          description: "",
          price: "",
          stock_quantity: "",
          image_url: "",
        });
        setError("");
      } else {
        const err = await res.json();
        setError(err.error || "Upload failed");
      }
    } catch (err) {
        console.error("Something went wrong:", err);
      setError("Network error");
    }
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2>🛒 Product Shop</h2>

      {isAdmin && (
        <form onSubmit={handleSubmit} style={{ marginBottom: "2rem" }}>
          <input
            name="name"
            placeholder="Product Name"
            value={formData.name}
            onChange={handleChange}
            required
          /><br />
          <textarea
            name="description"
            placeholder="Description"
            value={formData.description}
            onChange={handleChange}
            required
          /><br />
          <input
            name="price"
            type="number"
            placeholder="Price"
            value={formData.price}
            onChange={handleChange}
            required
          /><br />
          <input
            name="stock_quantity"
            type="number"
            placeholder="Stock Quantity"
            value={formData.stock_quantity}
            onChange={handleChange}
            required
          /><br />
          <input
            name="image_url"
            placeholder="Image URL"
            value={formData.image_url}
            onChange={handleChange}
            required
          /><br />
          <button type="submit">Upload Product</button>
        </form>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div>
        <h3>📦 Available Products</h3>
        {products.length === 0 ? (
          <p>No products found.</p>
        ) : (
          <ul>
            {products.map((p) => (
              <li key={p.id} style={{ marginBottom: "1rem" }}>
                <strong>{p.name}</strong><br />
                <img src={p.image_url} alt={p.name} width="100" /><br />
                <em>{p.description}</em><br />
                Price: ${p.price} | In Stock: {p.stock_quantity}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default Shop;
