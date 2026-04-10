"use client";
import { useState, useEffect } from 'react';
import TopNav from '@/components/TopNav';
import RestaurantCard from '@/components/RestaurantCard';

export default function Home() {
  const [locations, setLocations] = useState([]);
  const [location, setLocation] = useState('');
  const [cuisine, setCuisine] = useState('chinese');
  const [budget, setBudget] = useState(2000);
  const [rating, setRating] = useState(4.0);
  const [preferences, setPreferences] = useState('');
  
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch available locations from python metadata api on load
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/metadata')
      .then(res => res.json())
      .then(data => {
        if(data.locations) setLocations(data.locations);
      })
      .catch(err => console.error("FastAPI Backend not available:", err));
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults([]);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: location,
          budget_max: Number(budget),
          cuisine: cuisine,
          min_rating: Number(rating),
          additional_preferences: preferences
        })
      });
      const data = await res.json();
      
      if(data.detail) throw new Error(data.detail);
      setResults(data);
    } catch(err) {
      setError(err.message || 'Error occurred hooking into Phase 4 pipeline. Ensure FastAPI server is running!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{height: '100%', display: 'flex', flexDirection: 'column'}}>
      <TopNav locations={locations} selectedLocation={location} setLocation={setLocation} />
      
      {/* Dynamic Data Routing to Backend */}
      <form className="filter-bar" onSubmit={handleSearch}>
        <input className="settings-select" placeholder="Cuisine (e.g. thai, italian)" value={cuisine} onChange={e => setCuisine(e.target.value)} required />
        <input type="number" className="settings-select" placeholder="Max Budget (₹)" value={budget} onChange={e => setBudget(e.target.value)} required style={{width: '140px'}}/>
        <input type="number" step="0.1" className="settings-select" placeholder="Min Rating" value={rating} onChange={e => setRating(e.target.value)} required style={{width: '120px'}}/>
        <input className="settings-select" style={{flexGrow: 1}} placeholder="Tell the AI what vibe you want (e.g. romantic, dim lighting, pet friendly)..." value={preferences} onChange={e => setPreferences(e.target.value)} />
        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Analyzing...' : 'Find Matches'}
        </button>
      </form>

      <div className="content-inner">
        {error && <div style={{color: 'white', backgroundColor: '#e23744', padding: '15px', borderRadius: '8px', marginBottom: '20px'}}>{error}</div>}
        
        <div className="results-grid">
          {results.length === 0 && !loading && !error && (
            <div style={{color: '#888', fontStyle: 'italic', fontSize: '1.1rem', marginTop: '40px', width: '100%', textAlign: 'center'}}>
              Enter your preferences above to see AI curated restaurants here. <br/><br/>
              (Try Location: <b>banashankari</b>, Cuisine: <b>chinese</b>, Vibes: <b>romantic</b>)
            </div>
          )}
          {results.length === 0 && loading && (
            <div style={{color: '#e23744', fontSize: '1.2rem', marginTop: '40px', width: '100%', textAlign: 'center', fontWeight: 'bold'}}>
              🧠 Groq LLM is currently evaluating your perfect restaurants...
            </div>
          )}
          {results.map((r, idx) => (
            <RestaurantCard key={idx} restaurant={r} />
          ))}
        </div>
      </div>
    </div>
  );
}
