import os
from pathlib import Path
import psycopg
from pgvector.psycopg import register_vector


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set")

    sql_path = Path(__file__).parent / "init_db.sql"
    sql = sql_path.read_text(encoding="utf-8")

    with psycopg.connect(database_url) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


if __name__ == "__main__":
    main()
