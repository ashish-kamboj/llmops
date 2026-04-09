"""Generate dummy users and realistic clickstream data for personalization."""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import psycopg
from pgvector.psycopg import register_vector

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
PAGES_DIR = DATA_DIR / "pages"

USERS = [
    {"id": "user-001", "name": "Alice", "team": "Engineering"},
    {"id": "user-002", "name": "Bob", "team": "Product"},
    {"id": "user-003", "name": "Carol", "team": "Design"},
    {"id": "user-004", "name": "Dave", "team": "Engineering"},
    {"id": "user-005", "name": "Eve", "team": "Data"},
]

# Topic affinity per team — higher weight = more likely to click pages under that topic
TEAM_TOPIC_AFFINITY = {
    "Engineering": {
        "API Guidelines": 5, "Platform Reliability": 5,
        "Architecture Decision Records": 4, "Release Management": 3,
        "Security Standards": 3, "Incident Response": 4,
        "Engineering Onboarding": 3,
    },
    "Product": {
        "Product Roadmaps": 5, "Sprint Rituals": 5,
        "Customer Support": 4, "Release Management": 3,
        "Data Governance": 2,
    },
    "Design": {
        "Design Systems": 5, "Product Roadmaps": 3,
        "Sprint Rituals": 3, "Customer Support": 3,
        "Engineering Onboarding": 2,
    },
    "Data": {
        "Data Governance": 5, "Platform Reliability": 3,
        "Architecture Decision Records": 3, "API Guidelines": 3,
        "Security Standards": 2,
    },
}

DEFAULT_AFFINITY = 1


def load_pages() -> list[dict]:
    pages_file = PAGES_DIR / "pages.json"
    if not pages_file.exists():
        raise SystemExit("pages.json not found. Run generate_pages.py first.")
    return json.loads(pages_file.read_text(encoding="utf-8"))


def generate_events(pages: list[dict], num_events: int = 200) -> list[dict]:
    random.seed(99)
    now = datetime.utcnow()
    events = []

    for _ in range(num_events):
        user = random.choice(USERS)
        team = user["team"]
        affinities = TEAM_TOPIC_AFFINITY.get(team, {})

        weights = []
        for page in pages:
            w = affinities.get(page["topic"], DEFAULT_AFFINITY)
            weights.append(w)

        page = random.choices(pages, weights=weights, k=1)[0]

        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        ts = now - timedelta(days=days_ago, hours=hours_ago)

        event_type = random.choices(
            ["view", "click_related"], weights=[0.7, 0.3], k=1
        )[0]

        events.append({
            "user_id": user["id"],
            "page_id": page["id"],
            "event_type": event_type,
            "created_at": ts.isoformat(),
        })

    return events


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set")

    pages = load_pages()
    events = generate_events(pages, num_events=200)

    with psycopg.connect(database_url) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            # Upsert users
            for user in USERS:
                cur.execute(
                    """
                    INSERT INTO users (id, name, team)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        team = EXCLUDED.team
                    """,
                    (user["id"], user["name"], user["team"]),
                )

            # Insert click events (clear old seed data first)
            cur.execute("DELETE FROM click_events")
            for ev in events:
                cur.execute(
                    """
                    INSERT INTO click_events (user_id, page_id, event_type, created_at)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (ev["user_id"], ev["page_id"], ev["event_type"], ev["created_at"]),
                )

        conn.commit()
    print(f"Seeded {len(USERS)} users and {len(events)} click events.")


if __name__ == "__main__":
    main()
