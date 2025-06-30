import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from "./Auth";

function AdminProductManagement() {
  const { user, token, logout } = useContext(AuthContext);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [stockQuantity, setStockQuantity] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [formMessage, setFormMessage] = useState('');

  const API_BASE_URL = "http://localhost:5555";

  useEffect(() => {
    if (user && user.role === 'admin' && token) {
      fetchProducts();
    } else if (!user || user.role !== 'admin') {
      setError('You must be logged in as an admin to view this page.');
      setLoading(false);
    } else if (user && user.role === 'admin' && !token) {
      setError('Authentication token missing. Please log in again.');
      setLoading(false);
      logout();
    }
  }, [user, token, logout]);

  const fetchProducts = () => {
    setLoading(true);
    setError('');

    if (!token) {
      setError('Authentication token is missing.');
      setLoading(false);
      return;
    }

    fetch(`${API_BASE_URL}/products`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then(response => {
        if (!response.ok) {
          return response.json().then(errorData => {
            throw new Error(errorData.message || 'Failed to fetch products');
          });
        }
        return response.json();
      })
      .then(data => {
        setProducts(data);
      })
      .catch(err => {
        setError(err.message || 'An unexpected error occurred.');
        console.error("Error fetching products:", err);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const resetForm = () => {
    setName('');
    setDescription('');
    setPrice('');
    setStockQuantity('');
    setImageUrl('');
    setFormMessage('');
    setEditingProduct(null);
  };

  const handleAddEditSubmit = (e) => {
    e.preventDefault();
    setFormMessage('');
  
    if (!name.trim() || !description.trim() || !price || !stockQuantity || !imageUrl.trim()) {
      setFormMessage('Please fill in all fields.');
      return;
    }
  
    const parsedPrice = parseFloat(price);
    const parsedStock = parseInt(stockQuantity, 10);
  
    if (isNaN(parsedPrice) || parsedPrice <= 0) {
      setFormMessage('Price must be a valid positive number.');
      return;
    }
  
    if (isNaN(parsedStock) || parsedStock < 0) {
      setFormMessage('Stock quantity must be a valid non-negative number.');
      return;
    }
  
    const urlRegex = /^(https?:\/\/.*\.(?:png|jpg|jpeg|gif|svg))$/i;
    if (!urlRegex.test(imageUrl.trim())) {
      setFormMessage('Image URL must be a valid URL.');
      return;
    }
  
    if (!token) {
      setFormMessage('Authentication token is missing. Please log in.');
      return;
    }
  
    const payload = {
      name: name.trim(),
      description: description.trim(),
      price: parsedPrice,
      stock_quantity: parsedStock,
      image_url: imageUrl.trim(),
    };
  
    console.log("Submitting product payload:", payload);
  
    const method = editingProduct ? 'PATCH' : 'POST';
    const url = editingProduct ? `${API_BASE_URL}/products/${editingProduct.id}` : `${API_BASE_URL}/products`;
  
    fetch(url, {
      method: method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    })
      .then(response => {
        if (!response.ok) {
          return response.json().then(errorData => {
            throw new Error(errorData.error || 'Failed to submit');
          });
        }
        return response.json();
      })
      .then(() => {
        setFormMessage(`Product ${editingProduct ? 'updated' : 'added'} successfully!`);
        fetchProducts();
        resetForm();
        setShowAddForm(false);
      })
      .catch(err => {
        setFormMessage(err.message || 'An unexpected error occurred.');
        console.error("Error adding/editing product:", err);
      });
  };

  const handleEditClick = (product) => {
    setEditingProduct(product);
    setName(product.name);
    setDescription(product.description);
    setPrice(product.price);
    setStockQuantity(product.stock_quantity);
    setImageUrl(product.image_url);
    setShowAddForm(true);
  };

  const handleDeleteClick = (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) {
      return;
    }
    setError('');
    if (!token) {
      setError('Authentication token is missing. Please log in.');
      return;
    }

    fetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'DELETE',
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then(response => {
        if (!response.ok) {
          return response.json().then(errorData => {
            throw new Error(errorData.error || 'Failed to delete product');
          });
        }
        return response.json();
      })
      .then(data => {
        alert(data.message || 'Product deleted successfully!');
        fetchProducts();
      })
      .catch(err => {
        setError(err.message || 'An unexpected error occurred.');
        console.error("Error deleting product:", err);
      });
  };

  if (loading) return <p>Loading admin panel...</p>;
  if (error) return <p className="error-message">{error}</p>;
  if (!user || user.role !== 'admin') return <p className="error-message">Access Denied. Admins only.</p>;

  return (
    <div className="admin-product-management">
      <h2 className="section-title">Admin Product Management</h2>

      <button onClick={() => { setShowAddForm(!showAddForm); resetForm(); }}>
        {showAddForm ? 'Cancel Add/Edit' : 'Add New Product'}
      </button>

      {showAddForm && (
  <div className="product-form-container">
    <h3>{editingProduct ? 'Edit Product' : 'Add New Product'}</h3>
    <form onSubmit={handleAddEditSubmit} className="product-form">
      <input
        type="text"
        placeholder="Product Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />
      <textarea
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
      ></textarea>
      <input
        type="number"
        placeholder="Price"
        value={price}
        onChange={(e) => setPrice(e.target.value)}
        step="0.01"
        min="0"
        required
      />
      <input
        type="number"
        placeholder="Stock Quantity"
        value={stockQuantity}
        onChange={(e) => setStockQuantity(e.target.value)}
        min="0"
        required
      />
      <input
        type="text"
        placeholder="Image URL"
        value={imageUrl}
        onChange={(e) => setImageUrl(e.target.value)}
        required
      />
      <button type="submit">{editingProduct ? 'Update Product' : 'Add Product'}</button>
      {formMessage && <p className="form-message">{formMessage}</p>}
    </form>
  </div>
)}

      <hr />

      <h3>Current Products</h3>
      <div className="product-list-admin">
        {products.length === 0 ? (
          <p>No products found.</p>
        ) : (
          products.map(product => (
            <div key={product.id} className="product-item-admin">
              <img src={product.image_url} alt={product.name} className="product-thumb" />
              <div className="details">
                <h4>{product.name} (KES {product.price.toLocaleString()})</h4>
                <p>Stock: {product.stock_quantity}</p>
                <p>{product.description.substring(0, 70)}...</p>
              </div>
              <div className="actions">
                <button onClick={() => handleEditClick(product)}>Edit</button>
                <button onClick={() => handleDeleteClick(product.id)} className="delete-btn">Delete</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default AdminProductManagement;