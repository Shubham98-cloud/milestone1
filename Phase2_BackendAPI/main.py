from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import sys
import os
from contextlib import contextmanager

# Add parent directory to path to import Phase 3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Phase3_LLMEngine.llm_service import rank_restaurants

app = FastAPI(title="Zomato Recommendation API", version="1.0.0")

# Enable CORS for Next.js frontend communication (Running on :3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite Database connection
DB_PATH = '../Phase1_DataIngestion/restaurants.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Pydantic models for explicit schema definition
class RecommendationRequest(BaseModel):
    location: str
    budget_max: int
    cuisine: str
    min_rating: float
    additional_preferences: Optional[str] = None

class AIRecommendationResponse(BaseModel):
    restaurant_id: int
    name: str
    cuisine: str
    estimated_cost: int
    rating: float
    ai_explanation: str

@app.get("/api/metadata")
def get_metadata():
    """Returns available bounding data (locations, cuisines, max cost) for UI building."""
    try:
        with get_db_connection() as conn:
            # We fetch unique lists to populate the frontend dropdowns intelligently
            locations = [row[0] for row in conn.execute("SELECT DISTINCT location FROM restaurants WHERE location IS NOT NULL").fetchall()]
            cuisines_raw = [row[0] for row in conn.execute("SELECT DISTINCT cuisine FROM restaurants WHERE cuisine IS NOT NULL").fetchall()]
            
            # Max cost calculation for frontend sliders
            max_cost = conn.execute("SELECT MAX(cost) FROM restaurants").fetchone()[0]
            
            return {
                "locations": sorted(locations),
                "cuisines": sorted(cuisines_raw),
                "max_cost": max_cost or 0
            }
    except Exception as e:
        # Before data_loader.py has been executed, this will fail. Return empty list if table doesn't exist
        if "no such table" in str(e).lower():
            return {"locations": [], "cuisines": [], "max_cost": 0, "message": "Database not initialized. Run data_loader.py first."}
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend", response_model=List[AIRecommendationResponse])
def recommend_restaurants(req: RecommendationRequest):
    """Filters the restaurants based on hard constraints and returns top 15 matches."""
    try:
        with get_db_connection() as conn:
            # Robust, parameterized query to safely filter matching restaurants
            query = """
                SELECT id, name, location, cuisine, cost, rating 
                FROM restaurants 
                WHERE location = ? 
                  AND cost <= ? 
                  AND rating >= ? 
                  AND cuisine LIKE ? 
                ORDER BY rating DESC 
                LIMIT 15
            """
            
            # LIKE operator allows us to match substring cuisines (e.g., 'Italian' matches 'Italian, Continental')
            cuisine_pattern = f"%{req.cuisine.lower()}%"
            
            cursor = conn.execute(query, (req.location.lower(), req.budget_max, req.min_rating, cuisine_pattern))
            rows = cursor.fetchall()
            
            restaurants = [dict(row) for row in rows]
            
            # Phase 4 Integration: Pass SQL filtered candidates to Groq LLM
            ai_ranked_results = rank_restaurants(req.model_dump(), restaurants)
            return ai_ranked_results
    except Exception as e:
        if "no such table" in str(e).lower():
            raise HTTPException(status_code=400, detail="Database not initialized. Please run data_loader.py first.")
        raise HTTPException(status_code=500, detail=str(e))
