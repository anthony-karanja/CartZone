import React from "react"; 

function Home() {
     return ( <div className="home-wrapper"> <div className="hero"> <div className="hero-text"> <h1>Welcome to CartZone</h1> <p>Your one-stop shop for everything you love. Affordable, reliable, and stylish.</p> <button className="hero-btn">Shop Now</button> </div> </div>

<div className="features">
    <h2>Why Shop With Us?</h2>
    <div className="feature-cards">
      <div className="feature-card">
        <h3>Fast Delivery</h3>
        <p>We deliver your orders quickly and on time.</p>
      </div>
      <div className="feature-card">
        <h3>Trusted Products</h3>
        <p>All our items are verified and high quality.</p>
      </div>
      <div className="feature-card">
        <h3>Affordable Prices</h3>
        <p>Shop top products at competitive prices.</p>
      </div>
    </div>
  </div>
</div>

); }

export default Home;