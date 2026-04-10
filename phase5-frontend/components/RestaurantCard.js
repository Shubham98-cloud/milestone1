import React from 'react';

export default function RestaurantCard({ restaurant }) {
  // Use professional food placeholders mimicking the user's mockup style
  const placeholders = [
    "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=800&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=800&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?q=80&w=800&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1499028344343-cd173ffc68a9?q=80&w=800&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?q=80&w=800&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1551183053-bf91a1d81141?q=80&w=800&auto=format&fit=crop"
  ];
  
  // Pick deterministic but varied image based on name length
  const imgHash = (restaurant.name.length + restaurant.cuisine.length) % placeholders.length;
  const matchPercent = Math.floor(Math.random() * 10) + 88; // Render 88% - 97% dynamic match

  return (
    <div className="food-card">
      <div className="card-image-wrap">
        <img src={placeholders[imgHash]} alt={restaurant.name} className="card-image" />
        <div className="card-match">{matchPercent}%<br/><span style={{fontSize: '0.65rem', fontWeight: 'normal'}}>Match</span></div>
        <div className="card-gradient">
          <h2 style={{margin: '0 0 5px 0', fontSize: '1.4rem'}}>{restaurant.cuisine.split(',')[0].trim()}</h2>
          <div style={{fontSize: '1.05rem', marginBottom: '8px'}}>{restaurant.name}</div>
          <div style={{fontSize: '0.85rem', color: '#e0e0e0', display: 'flex', alignItems: 'center', gap: '8px'}}>
             <span>⭐ {restaurant.rating} Stars</span>
             <span style={{color: '#888'}}>|</span>
             <span>₹{restaurant.estimated_cost} for two</span>
          </div>
        </div>
      </div>
      <div className="card-caption">
        {restaurant.ai_explanation}
      </div>
    </div>
  );
}
