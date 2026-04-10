from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Phase2_BackendAPI.main import app
import json

client = TestClient(app)

print("--- Running Test Case 1: Fetch Metadata ---")
metadata_res = client.get("/api/metadata")
print(f"Status: {metadata_res.status_code}")
if metadata_res.status_code == 200:
    data = metadata_res.json()
    print(f"Loaded {len(data.get('locations', []))} locations and {len(data.get('cuisines', []))} cuisines. Max cost: {data.get('max_cost')}")

print("\n--- Running Test Case 2: Standard Recommendation Request (Banashankari, Chinese) ---")
payload_1 = {
    "location": "banashankari",
    "budget_max": 2000,
    "cuisine": "chinese",
    "min_rating": 4.0,
    "additional_preferences": "romantic, dim lighting"
}
rec_res_1 = client.post("/api/recommend", json=payload_1)
print(f"Status: {rec_res_1.status_code}")
if rec_res_1.status_code == 200:
    print("AI Recommendations:")
    print(json.dumps(rec_res_1.json(), indent=2))
else:
    print(f"Error: {rec_res_1.json()}")

print("\n--- Running Test Case 3: Empty Filter Case (Overconstrained) ---")
# Choosing a budget too low and rating too high. DB should return nothing.
payload_2 = {
    "location": "delhi",
    "budget_max": 100, 
    "cuisine": "italian",
    "min_rating": 4.9
}
rec_res_2 = client.post("/api/recommend", json=payload_2)
print(f"Status: {rec_res_2.status_code}")
print("Response:", rec_res_2.json())
