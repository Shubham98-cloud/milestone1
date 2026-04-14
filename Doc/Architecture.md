# Detailed Phase-Wise Architecture Plan

This document breaks down the technical architecture, data flows, and code structures required to build the AI-Powered Restaurant Recommendation System.

---

## Phase 1: Data Ingestion & Storage Layer

**Objective:** Pull the unstructured/semi-structured CSV/JSON data from HuggingFace, clean it, and store it in a query-optimized local database.

### 1.1 Data Extraction Component
*   **Library:** `datasets` (from HuggingFace).
*   **Action:** Script `data_loader.py` will execute `load_dataset('ManikaSaini/zomato-restaurant-recommendation')` and convert it to a Pandas DataFrame.

### 1.2 Data Transformation Component (Pandas)
*   **Normalization:** 
    *   Lowercase all text in the `location` and `cuisine` columns for case-insensitive matching.
    *   Parse the `cost` column (e.g., removing currency symbols or commas, converting to `Integer`).
    *   Parse the `rating` column (handling "NEW", "-", or missing values by converting them to `NULL` or floats).
*   **Structuring:** Split comma-separated cuisines into queryable formats or keep them as string aggregations for `LIKE` queries.

### 1.3 Data Storage Component
*   **Technology:** **SQLite** via SQLAlchemy.
*   **Schema (Table: `restaurants`):**
    *   `id` (Primary Key, Auto-increment)
    *   `name` (String)
    *   `location` (String, Indexed for fast lookups)
    *   `cuisine` (String)
    *   `cost` (Integer, Indexed for budget filtering)
    *   `rating` (Float, Indexed for rating filters)
    *   `url` (String, if available)
*   **Workflow:** Run the ingestion script once during environment setup to populate the `restaurants.db` file.

---

## Phase 2: Core Filtering Logic & Backend Service

**Objective:** Handle user requests and drastically reduce the number of potential restaurants (using SQL queries) before passing them to the expensive LLM layer.

### 2.1 API Framework (FastAPI)
*   **Why FastAPI:** Asynchronous, natively supports Pydantic validation, and integrates perfectly with Python LLM stacks.
*   **Endpoints:**
    *   `GET /api/metadata`: Returns unique bounds (all cities, max cost, cuisine types) to populate the frontend UI dropdowns without hardcoding them.
    *   `POST /api/recommend`: The main execution endpoint.

### 2.2 Recommender Service Module
*   **Input Data Model (Pydantic):**
    ```python
    class RecommendationRequest(BaseModel):
        location: str
        budget_max: int
        cuisine: str
        min_rating: float
        additional_preferences: str = None  # e.g., "outdoor seating"
    ```
*   **SQL Filtering Logic:**
    *   Query the SQLite database using the hard constraints: `SELECT * FROM restaurants WHERE location = {location} AND cost <= {budget_max} AND rating >= {min_rating} AND cuisine LIKE '%{cuisine}%' ORDER BY rating DESC LIMIT 15`.
    *   *Result:* A lightweight JSON array of max 15 restaurants perfectly matching the user's base criteria.

---

## Phase 3: AI/LLM Recommendation Engine

**Objective:** Use Generative AI to act as a food critic. Rank the SQL-filtered shortlist and provide tailored, human-like summaries on why they match the user's specific desires (especially `additional_preferences`).

### 3.1 Provider Setup
*   **Provider:** Groq LLM
*   **Authentication:** The API key will be stored securely in a local `.env` file.

### 3.2 Prompt Engineering & Chain setup
*   **System Prompt:** *"You are an expert, local food critic. You will be provided with user constraints and a JSON list of candidate restaurants. Your job is to select the TOP 3 restaurants from this list that best fit the user's profile, rank them, and write a unique 2-sentence explanation for each outlining why it's a perfect match based on their specific request."*
*   **Input Payload to LLM:** 
    ```json
    { "user_preferences": "...", "database_candidates": [ { "name": "...", "rating": 4.5, "cost": 800 } ] }
    ```

### 3.3 Output Parsing (Structured Output)
*   **Method:** We will use Native Function Calling or Structured Outputs (or robust prompt parsing) to force the Groq LLM to return valid JSON instead of markdown text.
*   **Target Output Schema:**
    ```json
    [
      {
        "restaurant_id": 12,
        "name": "Pizza Haven",
        "cuisine": "Italian",
        "rating": 4.5,
        "estimated_cost": 800,
        "ai_explanation": "Pizza Haven is highly rated for authentic Italian in Delhi. It fits perfectly under your budget while offering the lively, family-friendly atmosphere you requested."
      }
    ]
    ```

---

## Phase 4: Full Backend API Integration & Architecture

**Objective:** Wire the Phase 2 FastAPI endpoints with the Phase 3 Groq LLM logic to create a fully functional, testable backend pipeline.

### 4.1 Orchestrator
*   Update `POST /api/recommend` to execute the SQL query, format the results, and invoke `rank_restaurants()` from the LLM service.
*   Return the final AI-ranked JSON output back to the API client.

---

## Phase 5: Output Display (Next.js Frontend)

**Objective:** Create a premium, responsive Web UI to collect user inputs and beautifully display the LLM's tailored answers modeled after the modern Zomato reference design.

### 5.1 Technology Choice
*   **Framework:** **Next.js (React)** 
*   **Styling:** CSS Modules / Vanilla CSS (with modern aesthetics matching the reference design).

### 5.2 Component Layout Mapping (Reference `screen.png`)
*   `AppLayout`
    *   `SidebarLeft`: Contains the prominent Zomato logo, navigation items (Home, Dining, Nightlife, Zomaland, Profile), and the floating AI Assistant chat bubble at the top left.
    *   `MainContent`
        *   `TopNavigationBar`: Search input, Location dropdown selector, and User Profile avatar.
        *   `RecommendationGrid`: A horizontal/flex container holding the AI results.
            *   `ImageCard`: A rich media card featuring:
                *   A dynamic food background image.
                *   A dark gradient overlay holding the Title, Restaurant Name, Rating, and Distance.
                *   A red floating badge for "Match %" (e.g., 89% Match).
                *   A rich text caption area containing the Groq `ai_explanation`.

### 5.3 Data Flow Summary
1.  User enters preferences -> Next.js Frontend sends `POST https://<your-streamlit-backend-url>/api/recommend`.
2.  Next.js receives JSON array containing ratings and AI explanations.
3.  `RecommendationGrid` dynamically maps the response payload into the beautiful `ImageCard` styling.

---

## Phase 6: Deployment Architecture

**Objective:** Deploy the full-stack application by hosting the backend on Streamlit and the frontend on Vercel.

> [!WARNING]
> **Important Note on Streamlit Backend:** Streamlit Cloud is primarily designed for hosting Streamlit UI applications, not standalone FastAPI backend services. To deploy FastAPI on Streamlit Cloud, we will use a workaround wrapper script (e.g., `streamlit_app.py`) that acts as an entry point to launch the local `uvicorn` FastAPI server.

### 6.1 Frontend Deployment (Vercel)
*   **Platform:** Vercel
*   **Target:** The `phase5-frontend` Next.js application.
*   **Configuration:** Vercel will automatically detect the Next.js framework, install dependencies (`npm install`), and build the production output (`npm run build`).
*   **Environment Variables:** 
    *   `NEXT_PUBLIC_BACKEND_URL`: Set to the deployed Streamlit Backend URL.

### 6.2 Backend Deployment (Streamlit)
*   **Platform:** Streamlit Community Cloud
*   **Target:** The Phase 4 Python FastAPI backend and database engine.
*   **Configuration:** 
    *   A custom `streamlit_app.py` script will serve as the entry point, handling the launch of the FastAPI application.
    *   Dependencies from `requirements.txt` (`fastapi`, `uvicorn`, `sqlalchemy`, `groq`) will be automatically installed.
*   **CORS Configuration:** The backend will use `CORSMiddleware` to allow cross-origin requests securely from the Vercel frontend domain.
*   **Environment Variables:**
    *   `GROQ_API_KEY`: Stored securely in Streamlit Secrets.
