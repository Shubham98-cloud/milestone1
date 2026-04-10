import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

# Initialize Groq client
# Ensure your .env file has GROQ_API_KEY=your_api_key_here
try:
    client = Groq()
except Exception as e:
    client = None
    print(f"Warning: Groq client failed to initialize: {e}. Ensure GROQ_API_KEY is set in .env")

def rank_restaurants(user_preferences: dict, database_candidates: list) -> list:
    """
    Takes user preferences and a list of SQL-filtered restaurant candidates,
    sends them to Groq LLM, and returns the top 3 with personalized explanations.
    """
    if not database_candidates:
        return []
        
    if not client:
        raise ValueError("Groq client not initialized. Missing API key.")

    system_prompt = """You are an expert local food critic. You will be provided with user constraints and a JSON list of candidate restaurants.
Your job is to select the TOP 3 restaurants from this list that best fit the user's profile, rank them, and write a unique 2-sentence explanation for each outlining why it's a perfect match based on their specific preferences.

You MUST respond completely and strictly in the following JSON format:
{
  "recommendations": [
    {
      "restaurant_id": 12,
      "name": "Restaurant Name",
      "cuisine": "Cuisine Type",
      "rating": 4.5,
      "estimated_cost": 800,
      "ai_explanation": "..."
    }
  ]
}"""

    user_prompt = f"""
User Preferences:
{json.dumps(user_preferences, indent=2)}

Database Candidates (Select Top 3):
{json.dumps(database_candidates, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant", 
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        # Parse output
        raw_output = response.choices[0].message.content
        parsedJSON = json.loads(raw_output)
        
        return parsedJSON.get("recommendations", [])
        
    except Exception as e:
        print(f"Error during LLM generation: {str(e)}")
        # Fallback to returning original top 3 if LLM fails
        return database_candidates[:3]

# Quick local test block
if __name__ == "__main__":
    sample_prefs = {"location": "delhi", "budget_max": 1000, "additional_preferences": "outdoor seating family friendly"}
    sample_candidates = [
        {"id": 1, "name": "Pizza Haven", "cuisine": "Italian", "cost": 800, "rating": 4.5},
        {"id": 2, "name": "Burger Joint", "cuisine": "American", "cost": 500, "rating": 4.1},
        {"id": 3, "name": "Sushi World", "cuisine": "Japanese", "cost": 1200, "rating": 4.8},
        {"id": 4, "name": "Pasta Express", "cuisine": "Italian", "cost": 750, "rating": 4.2}
    ]
    
    # Try it out (will fail gracefully if no API key is set)
    try:
        print(json.dumps(rank_restaurants(sample_prefs, sample_candidates), indent=2))
    except Exception as e:
        print(f"Cannot run test: {e}")
