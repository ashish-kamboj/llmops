# Confluence-Style Related Content Recommender

This project builds a Confluence-like "Related content" recommender using Gemini embeddings, Postgres + pgvector, FastAPI, and Streamlit.

## What This Project Does

- Generates 36 synthetic Confluence-style HTML pages with realistic structure (headings, lists, tables, images).
- Extracts clean searchable text from those HTML pages.
- Creates Gemini embeddings for each page and stores them in PostgreSQL.
- Seeds 5 dummy users and ~200 clickstream events to enable personalized recommendations.
- Serves hybrid recommendations (semantic + click behavior + recency) through FastAPI.
- Renders a Confluence-like UI in Streamlit with user selector, left navigation, and related content cards.

## How It Works (End-to-End)

1. Data generation:
   - `src/pipelines/generate_pages.py` writes HTML pages and metadata under `data/pages`.
2. Text extraction:
   - `src/pipelines/extract_text.py` parses HTML and creates normalized text in `data/extracted/pages_text.json`.
3. Embedding + load:
   - `src/pipelines/embed_pages.py` calls Gemini embedding model (`models/gemini-embedding-001`), then upserts into:
     - `pages`
     - `page_text`
     - `page_embeddings`
4. Clickstream seeding:
   - `src/pipelines/generate_clickstream.py` creates 5 users across different teams and ~200 view/click events.
   - Click distribution is topic-weighted per team (engineers view more API/architecture pages, product people view roadmaps, etc.).
5. API retrieval:
   - `src/app/main.py` exposes `/pages`, `/pages/{page_id}`, `/recommend/{page_id}`, `/users`, and `/click`.
   - `/recommend/{page_id}?user_id=user-001` triggers hybrid ranking.
   - Without `user_id`, it falls back to semantic + recency only.
6. Hybrid ranking (`src/app/recommender.py`):
   - Pulls top-20 candidates by semantic similarity.
   - Computes per-candidate click score (60% personal history + 40% team-level co-visitation).
   - Computes recency score (exponential decay, 30-day half-life).
   - Blends: `0.5 * semantic + 0.3 * click + 0.2 * recency`.
   - Returns top-6.
7. UI:
   - `ui/streamlit_app.py` shows a user selector, page navigation, and related content cards with score breakdown.

## System Architecture

```text
            +------------------------------+
            | Synthetic HTML Pages         |
            | (data/pages/*.html)          |
            +--------------+---------------+
                           |
                           v
            +------------------------------+
            | Text Extraction Pipeline     |
            | extract_text.py              |
            +--------------+---------------+
                           |
                           v
            +------------------------------+
            | Embedding Pipeline           |
            | embed_pages.py + Gemini API  |
            +--------------+---------------+
                           |
                           v
            +------------------------------+
            | Clickstream Seeding          |
            | generate_clickstream.py      |
            +--------------+---------------+
                           |
                           v
            +------------------------------+
            | PostgreSQL + pgvector        |
            | pages / page_text /          |
            | page_embeddings / users /    |
            | click_events                 |
            +------+-----------------------+
                   |                       |
                   v                       v
      +------------------------+   +------------------------+
      | FastAPI                |   | Streamlit UI           |
      | Hybrid Recommender     |<--| User picker + pages +  |
      | /recommend?user_id=    |   | related content cards  |
      +------------------------+   +------------------------+
```

## Prerequisites

- Python 3.11
- Docker (recommended for PostgreSQL + pgvector)
- A Gemini API key

### PostgreSQL + pgvector Setup

Use one of the following options before running the application.

#### Option A: Docker (recommended)

Run PostgreSQL with pgvector in one command:

`docker run --name confluence_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=confluence_recommendation -p 5432:5432 -d pgvector/pgvector:pg16`

#### Option B: Ubuntu/WSL native install (PostgreSQL + pgvector)

1. Install PostgreSQL (example: v16)
   - `sudo apt update`
   - `sudo apt install -y postgresql postgresql-contrib`
   - `sudo service postgresql start`
2. Install pgvector package (if available in your distro repo)
   - `sudo apt install -y postgresql-16-pgvector`
3. If package is unavailable, install pgvector from source
   - `sudo apt install -y postgresql-server-dev-16 build-essential git`
   - `git clone https://github.com/pgvector/pgvector.git`
   - `cd pgvector`
   - `make`
   - `sudo make install`
4. Create database and enable extension
   - `sudo -u postgres psql -c "CREATE DATABASE confluence_recommendation;"`
   - `sudo -u postgres psql -d confluence_recommendation -c "CREATE EXTENSION IF NOT EXISTS vector;"`
5. Run project schema
   - `python scripts/init_db.py`

## Quick Start (Local)

1. Create and activate a Python 3.11 environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Create `.env` from `.env.example` and set at least:
   - `DATABASE_URL`
   - `GEMINI_API_KEY`
4. Set `DATABASE_URL` to your target database.
   - Example local value: `postgresql://postgres:postgres@localhost:5432/confluence_recommendation`
   - Default in code is `postgresql://postgres:postgres@localhost:5432/confluence_recommendation`.
5. Initialize schema:
   - `python scripts/init_db.py`
6. Generate pages:
   - `python src/pipelines/generate_pages.py`
7. Extract text:
   - `python src/pipelines/extract_text.py`
8. Create embeddings:
   - `python src/pipelines/embed_pages.py`
9. Seed users and clickstream:
   - `python src/pipelines/generate_clickstream.py`
10. Run API:\n    - `uvicorn src.app.main:app --host 0.0.0.0 --port 8000`\n11. Run UI:\n    - `streamlit run ui/streamlit_app.py`

Note: `page_embeddings` is `vector(3072)` because Gemini embedding output is 3072 dimensions. For this dimensionality, pgvector ANN index limits apply (>2000), so this project uses exact scan for recommendations.

## Docker (Local or AWS)

Docker Compose uses `confluence_recommendation` as the database name in `docker-compose.yml`.

1. Create `.env` from `.env.example` and set `GEMINI_API_KEY`.
2. Ensure `DATABASE_URL` in `.env` points to the Docker database service.
   - Example: `postgresql://postgres:postgres@db:5432/confluence_recommendation`
3. `docker compose up --build`
4. Initialize DB schema inside the API container:
   - `docker exec -it confluence_api python scripts/init_db.py`
5. Run pipeline steps inside the API container:
   - `docker exec -it confluence_api python src/pipelines/generate_pages.py`
   - `docker exec -it confluence_api python src/pipelines/extract_text.py`
   - `docker exec -it confluence_api python src/pipelines/embed_pages.py`
   - `docker exec -it confluence_api python src/pipelines/generate_clickstream.py`
6. Open:
   - API docs: `http://localhost:8000/docs`
   - UI: `http://localhost:8501`

## AWS Deployment (Summary)

- Use ECS or EC2 to run the Docker Compose stack.
- Set environment variables via AWS Secrets Manager or task definitions.
- Ensure port 8000 (API) and 8501 (UI) are reachable.

## Troubleshooting

### 1) `ImportError: attempted relative import with no known parent package`

Cause:
- Running `src/app/main.py` directly as a script.

Fix:
- Run as module or with uvicorn from repo root:
   - `python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000`

### 2) `ModuleNotFoundError: No module named 'src'`

Cause:
- Command not run from project root, or `PYTHONPATH` is missing.

Fix:
- Open terminal at repo root (`d:\attlasian-recommendation`) and run:
   - `python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000`

### 3) `ValidationError ... api_base_url extra_forbidden`

Cause:
- `.env` has `API_BASE_URL` but settings model did not accept extra fields.

Fix:
- Already fixed in `src/app/config.py` by adding `api_base_url` and allowing extra env vars.

### 4) `database "confluence_reco" does not exist`

Cause:
- Old DB name in `.env` or command.

Fix:
- Use `confluence_recommendation` everywhere:
   - `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/confluence_recommendation`

### 5) `could not open extension control file ... vector.control`

Cause:
- `pgvector` extension is not installed on the PostgreSQL server.

Fix:
- Install pgvector for your PostgreSQL version (or build from source), then run:
   - `CREATE EXTENSION IF NOT EXISTS vector;`

### 6) `expected 768 dimensions, not 3072`

Cause:
- Embedding model output and DB vector column dimensions do not match.

Fix:
- Use Gemini model dimensions consistently:
   - `.env`: `EMBEDDING_DIM=3072`
   - DB column: `embedding vector(3072)`

### 7) `column cannot have more than 2000 dimensions for ivfflat/hnsw index`

Cause:
- pgvector ANN indexes have dimension limits lower than 3072.

Fix:
- For this project, keep `vector(3072)` without ANN index and use exact search (good for small datasets).
- For larger datasets, use a lower-dimensional embedding model or a dedicated vector database.

## Project Structure

- [src/app](src/app): FastAPI service and hybrid recommender
- [src/pipelines](src/pipelines): data generation, text extraction, embedding, and clickstream seeding
- [scripts](scripts): database initialization SQL/Python helpers
- [ui](ui): Streamlit UI with user selector and score breakdown
- [data](data): HTML pages and images
