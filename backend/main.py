# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import Dict, Any

# --- 1. FastAPI Application Initialization ---
app = FastAPI()

# --- 2. Configure CORS (Crucial for React <-> FastAPI communication) ---
# Allows the React frontend running on localhost:5173 (or similar) to talk to the backend.
# Add the origins where your frontend application runs.
origins = [
    "http://localhost:3000",  # Common React port
    "http://localhost:5173",  # Common Vite/React port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- 3. JobTech API Configuration ---
JOBTECH_API_URL = "https://jobsearch.api.jobtechdev.se/search"

HEADERS = {
    "User-Agent": "FastAPI Job Seeker App (Contact: your-name@example.com)",
    # **NEW FIX**: Explicitly request JSON data
    "Accept": "application/json"
}


@app.get("/api/jobs")
def get_latest_jobs() -> Dict[str, Any]:
    """
    Fetches the latest job ads for the 'Data/IT' occupation field in Stockholm.
    """
    IT_CONCEPT_ID = "apaJ_2ja_LuF"

    params = {
        # 1. Filter by Occupation Field ID (Data/IT)
        "occupation-field": IT_CONCEPT_ID,

        # 2. Add Location Filter
        "q": "Stockholm",

        # 3. Limit the results
        "limit": 10

        # REMOVED: No 'python' free text search
    }

    try:
        response = requests.get(JOBTECH_API_URL, params=params, headers=HEADERS)
        response.raise_for_status()

        data = response.json()
        job_list = data.get("hits", [])

        # Print to confirm the new, filtered query is working
        print(f"SUCCESS: Fetched {len(job_list)} jobs for 'Data/IT' in Stockholm.")

        # Return a simplified list of jobs
        simple_jobs = [
            {
                "id": job.get("id"),
                "title": job.get("headline"),
            }
            for job in job_list
        ]

        return {"status": "success", "data": simple_jobs, "count": len(job_list)}

    except requests.exceptions.RequestException as e:
        print(f"FAILURE: Error fetching data: {e}")
        return {"status": "error", "message": f"Error fetching data from JobTech API: {e}"}

TAXONOMY_API_URL = "https://taxonomy.api.jobtechdev.se/v1/taxonomy/main/concepts"


# backend/main.py (The corrected function)
# backend/main.py (The final, corrected function for ID lookup)

@app.get("/api/taxonomy/search")
def search_taxonomy(q: str = "IT") -> Dict[str, Any]:
    """
    Temporary endpoint to search the Taxonomy API for a concept ID.
    Example: http://127.0.0.1:8000/api/taxonomy/search?q=Data/IT
    """
    params = {
        "text": q,
        "type": "occupation-field",  # Filter only for occupation fields
        "limit": 5
    }

    try:
        response = requests.get(TAXONOMY_API_URL, params=params, headers=HEADERS)
        response.raise_for_status()

        data = None
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as json_e:
            error_msg = f"Taxonomy API returned non-JSON data. Error: {json_e}"
            print(f"JSON ERROR: {error_msg}")
            print(f"RAW RESPONSE TEXT: {response.text[:200]}...")
            return {"status": "error", "message": error_msg}

        # ------------------------------------------------------------------
        # FINAL FIX: Determine where the concepts list is located
        # ------------------------------------------------------------------
        concepts = []
        if isinstance(data, list):
            # If the top-level response is a list, that list *is* the concepts
            concepts = data
        elif isinstance(data, dict):
            # If the top-level response is a dict, get the 'concepts' key
            concepts = data.get("concepts", [])

        if not concepts:
            print("-" * 50)
            print(f"Taxonomy Search Results for '{q}':")
            print(f"  No occupation-field results found for '{q}'. Try a different query (e.g., 'Data').")
            print("-" * 50)
        else:
            # Print the relevant part of the response for easy debugging
            print("-" * 50)
            print(f"Taxonomy Search Results for '{q}':")
            for concept in concepts:
                # We also use .get() here in case 'id' or 'term' are missing
                print(f"  - ID: {concept.get('id', 'N/A')}, Term: {concept.get('term', 'N/A')}")
            print("-" * 50)

        return {"status": "success", "results": concepts}

    except requests.exceptions.RequestException as e:
        print(f"NETWORK ERROR: Error fetching taxonomy data: {e}")
        return {"status": "error", "message": f"Network Error: {e}"}