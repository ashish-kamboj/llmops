from typing import List, Dict, Any

from .db import get_conn


def get_similar_pages(page_id: str, k: int = 6) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.embedding
                FROM page_embeddings e
                WHERE e.page_id = %s
                """,
                (page_id,),
            )
            row = cur.fetchone()
            if not row:
                return []
            target_embedding = row[0]

            cur.execute(
                """
                SELECT p.id, p.title, p.html_path,
                       1 - (e.embedding <=> %s) AS similarity
                FROM page_embeddings e
                JOIN pages p ON p.id = e.page_id
                WHERE p.id <> %s
                ORDER BY e.embedding <=> %s
                LIMIT %s
                """,
                (target_embedding, page_id, target_embedding, k),
            )
            results = []
            for page_id, title, html_path, similarity in cur.fetchall():
                results.append(
                    {
                        "id": page_id,
                        "title": title,
                        "html_path": html_path,
                        "similarity": float(similarity),
                    }
                )
            return results
