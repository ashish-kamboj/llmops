-- =============================================================================
-- RAG CHATBOT: Document Ingestion Pipeline (Lakeflow SDP)
-- =============================================================================
-- This file defines the Lakeflow Spark Declarative Pipeline for ingesting,
-- parsing, and chunking PDF documents.
--
-- Pipeline Flow:
--   Volume (PDFs) → Bronze (Raw Binary) → Silver (Parsed Text) → Gold (Chunks)
--
-- Key Functions Used:
--   - read_files() with Auto Loader for incremental file ingestion
--   - ai_parse_document() for extracting text from PDFs
--   - ai_prep_search() for semantic chunking optimized for RAG
--
-- Attach this .sql file as source code to a Lakeflow Pipeline.
-- Pipeline Settings: Catalog=ashish_kamboj_rag, Schema=project_docs_rag, Channel=Preview
-- =============================================================================


-- =============================================================================
-- BRONZE LAYER: Raw Document Ingestion
-- =============================================================================
-- Reads PDF files as binary from the UC Volume using Auto Loader (streaming).
-- Auto Loader tracks which files have been processed, ensuring incremental loads.
-- New files uploaded to the Volume are automatically picked up on next pipeline run.
-- =============================================================================

CREATE OR REFRESH STREAMING TABLE bronze_raw_documents
COMMENT 'Raw binary content of PDF documents ingested from Volume'
AS SELECT 
  content,
  path AS file_path,
  element_at(split(path, '/'), -1) AS file_name,
  length AS file_size,
  modificationTime AS file_modification_time
FROM STREAM read_files(
  '/Volumes/ashish_kamboj_rag/project_docs_rag/raw_documents/',
  format => 'binaryFile',
  pathGlobFilter => '*.pdf'
);


-- =============================================================================
-- SILVER LAYER: Document Parsing
-- =============================================================================
-- Uses ai_parse_document() to extract structured text from raw PDF binary.
-- This function handles complex layouts, tables, and multi-column PDFs.
-- Output includes full document text with structural metadata.
-- =============================================================================

CREATE OR REFRESH STREAMING TABLE silver_parsed_documents
COMMENT 'Parsed document content extracted from PDFs using ai_parse_document'
AS SELECT
  file_name,
  file_path,
  file_size,
  file_modification_time,
  ai_parse_document(content, map('version', '2.0')) AS parsed_content
FROM STREAM(LIVE.bronze_raw_documents);


-- =============================================================================
-- GOLD LAYER: Semantic Chunking with ai_prep_search
-- =============================================================================
-- Transforms parsed documents into semantic chunks optimized for RAG retrieval.
-- Each chunk includes:
--   - chunk_id: Unique identifier for the chunk
--   - chunk_to_embed: Text optimized for embedding (includes context headers)
--   - chunk_to_retrieve: Text returned to the user (clean, readable)
--   - source_uri: Original file path for attribution
--
-- Chunking Strategy:
-- ai_prep_search uses a semantic chunking approach that:
--   1. Respects document structure (sections, paragraphs)
--   2. Enriches chunks with document-level context (titles, headers)
--   3. Produces embedding-ready text with contextual prefixes
--   4. Keeps chunks within optimal token limits for the embedding model
-- =============================================================================

CREATE OR REFRESH MATERIALIZED VIEW gold_document_chunks
COMMENT 'Semantic chunks ready for Vector Search indexing'
AS 
WITH prepped_documents AS (
  SELECT
    file_name,
    file_path,
    ai_prep_search(parsed_content) AS result
  FROM LIVE.silver_parsed_documents
)
SELECT
  chunk.value:chunk_id::STRING AS chunk_id,
  chunk.value:chunk_position::INT AS chunk_position,
  chunk.value:chunk_to_retrieve::STRING AS chunk_to_retrieve,
  chunk.value:chunk_to_embed::STRING AS chunk_to_embed,
  prepped_documents.file_name AS source_file,
  prepped_documents.file_path AS source_uri
FROM
  prepped_documents,
  LATERAL variant_explode(prepped_documents.result:document.contents) AS chunk;


-- =============================================================================
-- DATA QUALITY: Validated Chunks View
-- =============================================================================
-- Apply quality constraints to ensure only valid chunks are indexed.
-- This prevents empty or malformed chunks from polluting the vector index.
-- =============================================================================

CREATE OR REFRESH MATERIALIZED VIEW gold_validated_chunks (
  CONSTRAINT valid_chunk_id EXPECT (chunk_id IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT valid_chunk_text EXPECT (chunk_to_embed IS NOT NULL AND LENGTH(chunk_to_embed) > 50) ON VIOLATION DROP ROW,
  CONSTRAINT valid_source EXPECT (source_file IS NOT NULL) ON VIOLATION DROP ROW
)
TBLPROPERTIES (delta.enableChangeDataFeed = true)
COMMENT 'Quality-validated chunks for Vector Search indexing'
AS SELECT * FROM LIVE.gold_document_chunks;
