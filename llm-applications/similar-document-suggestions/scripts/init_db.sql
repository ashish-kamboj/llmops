-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Pages metadata
CREATE TABLE IF NOT EXISTS pages (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    html_path TEXT NOT NULL,
    labels TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Extracted text
CREATE TABLE IF NOT EXISTS page_text (
    page_id TEXT PRIMARY KEY REFERENCES pages(id) ON DELETE CASCADE,
    content_text TEXT NOT NULL
);

-- Embeddings (no index due to pgvector 2000-dim limit)
CREATE TABLE IF NOT EXISTS page_embeddings (
    page_id TEXT PRIMARY KEY REFERENCES pages(id) ON DELETE CASCADE,
    embedding vector(3072) NOT NULL
);
