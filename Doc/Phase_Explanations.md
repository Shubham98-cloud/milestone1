# Zomato AI Recommendation System: End-to-End Architecture

This document provides a comprehensive explanation of how the Zomato AI platform operates—detailing both the overall project flow and the specific sequential execution phases that make the magic happen.

---

## 🚀 How the Project Works & Data Flow

At its core, this project is a hybrid "Search & Reasoning" pipeline. Traditional recommendation systems simply return a static list of restaurants based on hard limits (like budget or location). Our system takes it a massive step further by utilizing an advanced Large Language Model (Groq / LLaMA-3) to read the user's specific "soft" preferences (e.g., "I want dim lighting and a romantic vibe") and mathematically evaluates the restaurants to provide human-like recommendations.

### The End-to-End Data Pipeline
1. **User Interaction (Frontend)**
   The user opens the **Next.js Desktop UI** and enters their hard constraints (Location, Budget, Cuisine, Rating) and their soft preferences (Vibe/Atmosphere prompt) into the TopNav filter bar.
2. **REST API Transmission (Network Layer)**
   The Next.js React frontend packages these parameters into a secure JSON payload and dispatches a `POST` request to the local **FastAPI Backend Server** (`http://127.0.0.1:8000/api/recommend`).
3. **Hard SQL Filtering (Phase 2 - Database)**
   Before asking the AI anything, the Python server connects to our offline `restaurants.db` SQLite database (which was built using 10,000+ real records from HuggingFace in Phase 1). The database runs a highly optimized `SELECT` query utilizing the user's *hard limits* (strictly filtering out restaurants that are too expensive or poorly rated). This efficiently funnels thousands of restaurants down to only the **Top 15 candidates**.
4. **AI Reasoning (Phase 3 - LLM Engine)**
   The Python Orchestrator converts those 15 candidate rows into a string and passes them to the **Groq GenAI Model**, along with the user's *soft preferences* prompt. 
   The AI is instructed to act as an expert food critic. It reads the 15 candidates, reads the vibe prompt, selects the absolute best matches, and dynamically writes a specialized justification (`ai_explanation`) summarizing *why* each place is perfect for this specific user.
5. **JSON Return (Phase 4 - API Response)**
   Groq returns a strictly formatted JSON array containing the final, AI-approved restaurant list. FastAPI routes this finalized list back to the browser.
6. **UI Rendering (Phase 5 - Next.js)**
   The Next.js frontend intercepts the incoming JSON array and visually maps the data onto premium, dark-mode `ImageCard` components, showcasing the restaurant details alongside the human-like explanation.

---

## 📁 Breakdown of Development Phases

### Phase 1: Data Ingestion (`Phase1_DataIngestion/`)
**Purpose:** Handle raw data acquisition and preparation.
*   **What it does:** Downloads the raw Zomato restaurant dataset from HuggingFace, heavily cleans the data (parsing integers out of strings, normalizing missing values), and builds a structured, highly-queryable local SQLite Database (`restaurants.db`). 

### Phase 2: Backend API (`Phase2_BackendAPI/`)
**Purpose:** Provide the core API server and Database filtering layer.
*   **What it does:** Uses `FastAPI` to host internet endpoints. It reads user preferences (like Budget, Cuisine, Minimum Rating, Location) and runs a hard SQL query to slash the list of thousands of restaurants down to only the Top 15 matches.

### Phase 3: LLM Engine (`Phase3_LLMEngine/`)
**Purpose:** Add AI reasoning to the filtered data.
*   **What it does:** Hosts the integration with GenAI providers (specifically **Groq LLM**). It takes the 15 SQL-filtered restaurant rows and pushes them through a meticulously engineered Prompt, ordering the AI to adopt the persona of an expert food critic.

### Phase 4: Backend Integration (`Phase4_BackendIntegration/`)
**Purpose:** Verify that Phase 2 and Phase 3 interconnect successfully.
*   **What it does:** Contains validation scripts (like `test_backend.py`) designed to simulate a real user hitting the Phase 2 API, which subsequently invokes the Phase 3 LLM. 

### Phase 5: Frontend (`Phase5_Frontend/` or `phase5-frontend/`)
**Purpose:** The final user-facing interface.
*   **What it does:** Provides a modern, dark-mode styling web application natively built using **Next.js**. It features complex navigational components, dynamic React Image mapping, and asynchronous fetching logic interacting with the Core Python API via customized CORS integrations.
