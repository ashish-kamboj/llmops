"""Hybrid recommender: semantic similarity + click behavior + recency."""

from datetime import datetime, timezone
from typing import List, Dict, Any

from .db import get_conn

# Blending weights
W_SEMANTIC = 0.5
W_CLICK = 0.3
W_RECENCY = 0.2

# How many candidates to pull from semantic search before re-ranking
CANDIDATE_POOL = 20

# Recency half-life in days (page updated 30 days ago gets ~0.5 score)
RECENCY_HALF_LIFE_DAYS = 30.0


def _semantic_candidates(page_id: str, k: int) -> List[Dict[str, Any]]:
    """Return top-k semantically similar pages with cosine similarity."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT embedding FROM page_embeddings WHERE page_id = %s",
                (page_id,),
            )
            row = cur.fetchone()
            if not row:
                return []
            target = row[0]

            cur.execute(
                """
                SELECT p.id, p.title, p.html_path, p.updated_at,
                       1 - (e.embedding <=> %s) AS similarity
                FROM page_embeddings e
                JOIN pages p ON p.id = e.page_id
                WHERE p.id <> %s
                ORDER BY e.embedding <=> %s
                LIMIT %s
                """,
                (target, page_id, target, k),
            )
            return [
                {
                    "id": r[0],
                    "title": r[1],
                    "html_path": r[2],
                    "updated_at": r[3],
                    "semantic": float(r[4]),
                }
                for r in cur.fetchall()
            ]


def _click_scores(user_id: str, candidate_ids: List[str]) -> Dict[str, float]:
    """Score each candidate by how often this user interacted with it."""
    if not user_id or not candidate_ids:
        return {}

    with get_conn() as conn:
        with conn.cursor() as cur:
            # Get user's team
            cur.execute("SELECT team FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            team = row[0] if row else None

            # Personal click counts
            cur.execute(
                """
                SELECT page_id, COUNT(*) AS cnt
                FROM click_events
                WHERE user_id = %s AND page_id = ANY(%s)
                GROUP BY page_id
                """,
                (user_id, candidate_ids),
            )
            personal = {r[0]: r[1] for r in cur.fetchall()}

            # Team-level click counts (collaborative signal)
            team_counts: Dict[str, int] = {}
            if team:
                cur.execute(
                    """
                    SELECT ce.page_id, COUNT(*) AS cnt
                    FROM click_events ce
                    JOIN users u ON u.id = ce.user_id
                    WHERE u.team = %s AND ce.page_id = ANY(%s)
                    GROUP BY ce.page_id
                    """,
                    (team, candidate_ids),
                )
                team_counts = {r[0]: r[1] for r in cur.fetchall()}

    # Normalize: personal weight 0.6, team weight 0.4
    max_personal = max(personal.values()) if personal else 1
    max_team = max(team_counts.values()) if team_counts else 1

    scores: Dict[str, float] = {}
    for pid in candidate_ids:
        p = personal.get(pid, 0) / max_personal
        t = team_counts.get(pid, 0) / max_team
        scores[pid] = 0.6 * p + 0.4 * t

    return scores


def _recency_score(updated_at) -> float:
    """Exponential decay: 1.0 for just-updated, ~0.5 at half-life."""
    if updated_at is None:
        return 0.0
    now = datetime.now(timezone.utc)
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    age_days = max((now - updated_at).total_seconds() / 86400.0, 0.0)
    import math
    return math.exp(-0.693 * age_days / RECENCY_HALF_LIFE_DAYS)


def get_similar_pages(
    page_id: str, k: int = 6, user_id: str | None = None
) -> List[Dict[str, Any]]:
    """Hybrid ranking: semantic + click behavior + recency."""
    candidates = _semantic_candidates(page_id, k=CANDIDATE_POOL)
    if not candidates:
        return []

    candidate_ids = [c["id"] for c in candidates]
    click_scores = _click_scores(user_id, candidate_ids) if user_id else {}

    for c in candidates:
        sem = c["semantic"]
        clk = click_scores.get(c["id"], 0.0)
        rec = _recency_score(c["updated_at"])

        if user_id:
            c["score"] = W_SEMANTIC * sem + W_CLICK * clk + W_RECENCY * rec
        else:
            # No user context: semantic + recency only
            c["score"] = 0.7 * sem + 0.3 * rec

        c["similarity"] = round(c["score"], 4)
        c["semantic_score"] = round(sem, 4)
        c["click_score"] = round(clk, 4)
        c["recency_score"] = round(rec, 4)

    candidates.sort(key=lambda x: x["score"], reverse=True)

    return [
        {
            "id": c["id"],
            "title": c["title"],
            "html_path": c["html_path"],
            "similarity": c["similarity"],
            "semantic_score": c["semantic_score"],
            "click_score": c["click_score"],
            "recency_score": c["recency_score"],
        }
        for c in candidates[:k]
    ]
