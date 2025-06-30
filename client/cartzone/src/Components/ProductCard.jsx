import React, { useContext } from 'react';
import { AuthContext } from './Auth';

function ProductCard({ product }) {
  const { user, token } = useContext(AuthContext);

  const handleAddToCart = () => { 
    if (!user || !token) {
      alert('Please log in to add items to your cart.');
      return;
    }

    fetch('http://localhost:5555/cart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ product_id: product.id, quantity: 1 }),
      })
      .then(response => {
          if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(errorData.message || 'Failed to add item to cart');
            });
          }
          return response.json();
      })
      .then(data => {
        console.log('Item added to cart:', data);
        alert('Item added to cart!');
      })
      .catch(error => {
        // console.error('Error adding to cart:', error);
        alert(error.message);
      });
  };

  return (
    <div className="product-card">
      <img src={product.image_url} alt={product.name} />
      <h3>{product.name}</h3>
      <p>KES {product.price.toLocaleString()}</p>
      {user ? (
        <button onClick={handleAddToCart}>Add to Cart</button>
      ) : (
        <button disabled title="Log in to add to cart">Add to Cart</button>
      )}
    </div>
  );
}

export default ProductCard;