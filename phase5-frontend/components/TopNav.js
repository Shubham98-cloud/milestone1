import React from 'react';

export default function TopNav({ locations, selectedLocation, setLocation }) {
  return (
    <div className="top-bar">
      <input type="text" className="search-input" placeholder="🔍 Search restaurants, cuisines, dishes..." />
      <select 
        className="settings-select"
        value={selectedLocation}
        onChange={(e) => setLocation(e.target.value)}
        required
      >
        <option value="">📍 Select Location (e.g. Banashankari)</option>
        {locations.map((loc, idx) => (
          <option key={idx} value={loc}>{loc}</option>
        ))}
      </select>
      <div style={{ backgroundColor: '#e23744', color: 'white', width: '45px', height: '45px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', fontSize: '1.2rem', boxShadow: '0 4px 10px rgba(226, 55, 68, 0.4)' }}>
        👤
      </div>
    </div>
  );
}
