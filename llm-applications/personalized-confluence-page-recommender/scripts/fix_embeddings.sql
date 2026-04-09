-- Recreate page_embeddings table with 3072 dimension
DROP TABLE IF EXISTS page_embeddings CASCADE;

CREATE TABLE page_embeddings (
    page_id TEXT PRIMARY KEY REFERENCES pages(id) ON DELETE CASCADE,
    embedding vector(3072) NOT NULL
);

CREATE INDEX page_embeddings_idx
    ON page_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);
