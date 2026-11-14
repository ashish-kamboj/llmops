from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import get_conn
from .recommender import get_similar_pages

app = FastAPI(title="Confluence Related Content API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


data_dir = Path(settings.data_dir)


@app.get("/pages")
def list_pages() -> List[dict]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title FROM pages ORDER BY title")
            return [{"id": r[0], "title": r[1]} for r in cur.fetchall()]


@app.get("/pages/{page_id}")
def get_page(page_id: str) -> dict:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, html_path, labels FROM pages WHERE id = %s",
                (page_id,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Page not found")
            page_id, title, html_path, labels = row

    html_file = data_dir / html_path
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="HTML file not found")

    html = html_file.read_text(encoding="utf-8")
    return {
        "id": page_id,
        "title": title,
        "labels": labels or [],
        "html": html,
    }


@app.get("/recommend/{page_id}")
def recommend(page_id: str, k: int = 6) -> dict:
    results = get_similar_pages(page_id, k=k)
    return {"page_id": page_id, "results": results}
