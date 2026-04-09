import json
import os
from pathlib import Path
from typing import List

import google.generativeai as genai
import psycopg
from pgvector.psycopg import register_vector

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
EXTRACTED_PATH = DATA_DIR / "extracted" / "pages_text.json"


def chunk_text(text: str, max_chars: int = 2000) -> List[str]:
    chunks = []
    current = []
    current_len = 0

    for paragraph in text.split("\n"):
        if current_len + len(paragraph) + 1 > max_chars and current:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(paragraph)
        current_len += len(paragraph) + 1

    if current:
        chunks.append("\n".join(current))

    return chunks


def embed_text(model: str, text: str) -> List[float]:
    result = genai.embed_content(
        model=model,
        content=text,
        task_type="retrieval_document",
    )
    embedding = result.get("embedding")
    if not embedding:
        raise RuntimeError("Embedding not returned by Gemini API")
    return embedding


def average_embeddings(embeddings: List[List[float]]) -> List[float]:
    if len(embeddings) == 1:
        return embeddings[0]
    dim = len(embeddings[0])
    sums = [0.0] * dim
    for emb in embeddings:
        for i in range(dim):
            sums[i] += emb[i]
    return [s / len(embeddings) for s in sums]


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
    database_url = os.getenv("DATABASE_URL")

    if not api_key:
        raise SystemExit("GEMINI_API_KEY is not set")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set")
    if not EXTRACTED_PATH.exists():
        raise SystemExit("pages_text.json not found. Run extract_text.py first.")

    genai.configure(api_key=api_key)

    pages = json.loads(EXTRACTED_PATH.read_text(encoding="utf-8"))

    with psycopg.connect(database_url) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            for page in pages:
                chunks = chunk_text(page["text"])
                embeddings = [embed_text(model, chunk) for chunk in chunks]
                embedding = average_embeddings(embeddings)

                cur.execute(
                    """
                    INSERT INTO pages (id, title, html_path, labels)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        html_path = EXCLUDED.html_path,
                        labels = EXCLUDED.labels,
                        updated_at = now()
                    """,
                    (page["id"], page["title"], page["html_path"], page["labels"]),
                )

                cur.execute(
                    """
                    INSERT INTO page_text (page_id, content_text)
                    VALUES (%s, %s)
                    ON CONFLICT (page_id) DO UPDATE SET
                        content_text = EXCLUDED.content_text
                    """,
                    (page["id"], page["text"]),
                )

                cur.execute(
                    """
                    INSERT INTO page_embeddings (page_id, embedding)
                    VALUES (%s, %s)
                    ON CONFLICT (page_id) DO UPDATE SET
                        embedding = EXCLUDED.embedding
                    """,
                    (page["id"], embedding),
                )

        conn.commit()


if __name__ == "__main__":
    main()
