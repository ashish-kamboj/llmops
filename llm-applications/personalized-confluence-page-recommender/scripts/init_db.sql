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

-- Users
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    team TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Click / view events for personalization
CREATE TABLE IF NOT EXISTS click_events (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    page_id TEXT NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL DEFAULT 'view',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS click_events_user_idx ON click_events(user_id);
CREATE INDEX IF NOT EXISTS click_events_page_idx ON click_events(page_id);
