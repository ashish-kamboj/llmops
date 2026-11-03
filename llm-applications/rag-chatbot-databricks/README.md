# RAG Chatbot for Project Documentation

An end-to-end Retrieval-Augmented Generation (RAG) application built on Databricks that serves as an intelligent Q&A chatbot for project documentation. The system ingests PDF documents, builds a semantic search index, and provides accurate, source-attributed answers through a Streamlit chat interface.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA INGESTION LAYER                            │
│  UC Volume (PDFs) → Lakeflow SDP Pipeline                           │
│  [Bronze: Raw Binary] → [Silver: Parsed] → [Gold: Chunks]          │
│  Trigger: File Arrival on Volume (automatic)                        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      VECTOR SEARCH LAYER                            │
│  Delta Sync Index (Triggered Sync)                                  │
│  Embedding: system.ai.qwen3-embedding-0-6b (1024 dimensions)       │
│  Source: gold_validated_chunks → Auto-sync on pipeline run          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RAG SERVING LAYER                              │
│  Model Serving Endpoint: rag_project_docs_endpoint                  │
│  Chain: Vector Search Retriever → Claude Haiku 4.5 LLM             │
│  Features: MLflow Tracing, Inference Logging, Auto-scaling          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                              │
│  Streamlit Chat App → Databricks Apps                               │
│  Features: Chat history, Source attribution, Error handling          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Data Ingestion** | Lakeflow Spark Declarative Pipelines (SDP) |
| **Document Parsing** | `ai_parse_document()` (Databricks AI Function) |
| **Chunking** | `ai_prep_search()` (Semantic chunking for RAG) |
| **Embeddings** | `system.ai.qwen3-embedding-0-6b` (1024 dim) |
| **Vector Database** | Databricks AI Search (Delta Sync Index) |
| **LLM** | `system.ai.claude-haiku-4-5` |
| **Orchestration** | LangChain (LCEL) |
| **Model Registry** | MLflow + Unity Catalog |
| **Serving** | Databricks Model Serving |
| **Frontend** | Streamlit on Databricks Apps |
| **Observability** | MLflow Tracing + GenAI Evaluation |
| **Governance** | Unity Catalog (catalog, schema, volume) |
| **Automation** | Lakeflow Jobs with File Arrival Trigger |

---

## Project Structure

```
rag_chatbot/
│
├── README.md                      # This file
├── 00_config                      # Shared configuration parameters
├── 01_data_setup                  # Unity Catalog infrastructure setup
├── 02_ingestion_pipeline          # Lakeflow SDP pipeline (Bronze → Silver → Gold)
├── 03_vector_search_setup         # Vector Search endpoint & index creation
├── 04_rag_chain                   # RAG chain build, test, MLflow logging & deployment
├── 05_evaluation                  # MLflow GenAI evaluation (Relevance, Groundedness)
├── 06_deployment_guide            # Step-by-step deployment instructions
│
└── streamlit_app/                 # Frontend application
    ├── app.py                     # Streamlit chat interface
    ├── app.yaml                   # Databricks Apps configuration
    └── requirements.txt           # Python dependencies
```

---

## Notebook Descriptions

### `00_config` — Configuration Parameters
Centralized configuration for the entire pipeline. All notebooks reference this via `%run ./00_config`.

**Key parameters:**
- Unity Catalog: `ashish_kamboj_rag.project_docs_rag`
- Volume: `/Volumes/ashish_kamboj_rag/project_docs_rag/raw_documents/`
- Embedding model: `system.ai.qwen3-embedding-0-6b`
- LLM: `system.ai.claude-haiku-4-5`
- Retrieval: Top-5 chunks, temperature 0.1, max 2048 tokens

### `01_data_setup` — Infrastructure Setup
Creates Unity Catalog resources and populates the document Volume.

**Actions:**
1. Creates catalog and schema
2. Creates a managed Volume for PDF storage
3. Copies source documents from workspace to the Volume
4. Verifies file listing

### `02_ingestion_pipeline` — Lakeflow SDP Pipeline
A Spark Declarative Pipeline notebook (do NOT run interactively).

**Pipeline layers:**
- **Bronze** (`bronze_raw_documents`): Streams binary PDF content from Volume via Auto Loader
- **Silver** (`silver_parsed_documents`): Extracts structured text using `ai_parse_document()`
- **Gold** (`gold_document_chunks`): Produces semantic chunks via `ai_prep_search()`
- **Quality** (`gold_validated_chunks`): Applies data quality constraints (non-null chunk_id, min 50 chars, valid source)

### `03_vector_search_setup` — AI Search Configuration
Provisions the Vector Search infrastructure.

**Creates:**
- A Standard Vector Search endpoint (`rag_chatbot_vs_endpoint`)
- A Delta Sync Index with Databricks-managed embeddings
- Triggered sync mode (cost-efficient; syncs when pipeline runs)
- Includes a test similarity search for validation

### `04_rag_chain` — RAG Chain & Deployment
Builds, tests, and deploys the complete RAG chain.

**Workflow:**
1. Enables MLflow tracing (`mlflow.langchain.autolog()`)
2. Initializes Vector Search retriever + Claude Haiku 4.5 LLM
3. Builds LangChain LCEL chain with custom prompt template
4. Tests with sample questions
5. Logs model to MLflow with signature and parameters
6. Deploys to Model Serving endpoint with inference logging

### `05_evaluation` — RAG Quality Assessment
Evaluates the RAG system using MLflow's GenAI framework.

**Metrics:**
- **Relevance**: Are retrieved chunks relevant to the query?
- **Groundedness**: Is the answer faithful to the retrieved context?
- **Safety**: Does the answer avoid harmful content?

### `06_deployment_guide` — Deployment Instructions
Comprehensive guide covering all deployment steps, pipeline creation, job triggers, and the Streamlit app setup.

---

## Setup & Deployment

### Prerequisites

- Databricks workspace with Unity Catalog enabled
- Access to Foundation Model APIs (`system.ai.*`)
- Permissions to create catalogs, schemas, and volumes
- Databricks Apps enabled in the workspace

### Step-by-Step Deployment

| Step | Action | Notebook/Asset |
|------|--------|----------------|
| 1 | Run data infrastructure setup | `01_data_setup` |
| 2 | Create Lakeflow Pipeline (attach `02_ingestion_pipeline`) | Pipelines UI |
| 3 | Run the pipeline (processes PDFs → chunks) | Pipeline UI / Trigger |
| 4 | Create Vector Search endpoint and index | `03_vector_search_setup` |
| 5 | Build, test, and deploy RAG chain | `04_rag_chain` |
| 6 | Evaluate quality | `05_evaluation` |
| 7 | Deploy Streamlit app | Databricks Apps UI |

### Pipeline Configuration

| Setting | Value |
|---------|-------|
| **Pipeline Name** | `rag_document_ingestion` |
| **Source Notebook** | `02_ingestion_pipeline` |
| **Target Catalog** | `ashish_kamboj_rag` |
| **Target Schema** | `project_docs_rag` |
| **Pipeline Mode** | Triggered |
| **Channel** | Preview (required for AI Functions) |

### File Arrival Trigger

The pipeline is automated via a Lakeflow Job with a file arrival trigger:
- **Monitored path**: `/Volumes/ashish_kamboj_rag/project_docs_rag/raw_documents/`
- **Min interval**: 5 minutes between runs
- **Wait after change**: 60 seconds (batches rapid uploads)

> **Note**: Workspace folders do NOT support file arrival triggers. Documents must be uploaded to the UC Volume for automatic processing.

---

## Chunking Strategy

This project uses `ai_prep_search()` for semantic document chunking, which provides:

1. **Structure-aware splitting** — Respects document boundaries (sections, paragraphs, headers)
2. **Context enrichment** — Each chunk is prefixed with document title and section headers for better embedding quality
3. **Dual-text output**:
   - `chunk_to_embed`: Enriched text for high-quality embeddings
   - `chunk_to_retrieve`: Clean text for user-facing display
4. **Optimal token sizing** — Automatically sizes chunks within embedding model limits
5. **Unique IDs** — Each chunk gets a deterministic `chunk_id` for deduplication

This approach significantly outperforms naive fixed-size splitting for structured documentation.

---

## Data Quality

The pipeline enforces quality constraints before indexing:

| Constraint | Rule | Action |
|------------|------|--------|
| `valid_chunk_id` | `chunk_id IS NOT NULL` | Drop row |
| `valid_chunk_text` | `chunk_to_embed IS NOT NULL AND LENGTH > 50` | Drop row |
| `valid_source` | `source_file IS NOT NULL` | Drop row |

These prevent empty, malformed, or unattributable chunks from entering the vector index.

---

## Observability

### MLflow Tracing
- Enabled via `mlflow.langchain.autolog()`
- Every RAG invocation generates a trace capturing:
  - Input query
  - Retrieved chunks and similarity scores
  - Formatted prompt sent to LLM
  - Generated response
  - End-to-end latency

### Inference Logging
- Enabled on the Model Serving endpoint (`auto_capture_config`)
- All request/response pairs logged to a Delta table
- Useful for drift detection, usage analytics, and quality monitoring

### Evaluation
- Run `05_evaluation` to score the system against curated test questions
- Results viewable in the MLflow Experiment UI
- Supports iterative improvement: adjust retrieval params, prompt, or chunking based on scores

---

## Streamlit Application

The frontend lives in `streamlit_app/` and is deployed on Databricks Apps.

**Features:**
- Conversational chat interface with message history
- Calls the RAG Model Serving endpoint via REST API
- Automatic authentication via Databricks Apps (OAuth token injection)
- Error handling with user-friendly messages
- Sidebar with usage tips and system info

**Deployment:**
1. Navigate to Databricks Apps in the workspace
2. Create a new app pointing to `streamlit_app/` as source
3. The `app.yaml` configures the command, environment, and resource permissions
4. Authentication (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`) is injected automatically

---

## Configuration Reference

| Parameter | Value | Description |
|-----------|-------|-------------|
| `CATALOG_NAME` | `ashish_kamboj_rag` | Unity Catalog catalog |
| `SCHEMA_NAME` | `project_docs_rag` | Schema for all RAG assets |
| `VOLUME_NAME` | `raw_documents` | Volume for source PDFs |
| `VECTOR_SEARCH_ENDPOINT` | `rag_chatbot_vs_endpoint` | AI Search endpoint |
| `VECTOR_INDEX_NAME` | `ashish_kamboj_rag.project_docs_rag.gold_chunks_index` | Vector index |
| `EMBEDDING_MODEL` | `system.ai.qwen3-embedding-0-6b` | Embedding model (1024 dim) |
| `LLM_MODEL` | `system.ai.claude-haiku-4-5` | Chat completion model |
| `RAG_CHAIN_ENDPOINT` | `rag_project_docs_endpoint` | Serving endpoint |
| `NUM_RESULTS` | `5` | Top-K chunks retrieved |
| `TEMPERATURE` | `0.1` | LLM temperature (low for factual) |
| `MAX_TOKENS` | `2048` | Max response tokens |

---

## Source Documents

The system currently indexes 15 PDF documents covering:

- **CDNA-Broadcast**: Pipeline architecture, functional design, run/refresh process, sustain, end-to-end flow
- **CDNA-ComScore**: Pipeline overview and run/refresh process
- **CDNA-Fetch Likelihood**: Functional architecture, preprocessing, postprocessing
- **CDNA-Hispanic**: Household prediction and modeling
- **ECOMM-Hispanic**: Household prediction and modeling

To add new documents, upload PDFs to:
```
/Volumes/ashish_kamboj_rag/project_docs_rag/raw_documents/
```
The file arrival trigger will automatically process them.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Irrelevant retrievals | Increase `NUM_RESULTS` or review chunking quality |
| Incomplete answers | Increase `MAX_TOKENS`, check if relevant docs exist |
| Hallucinations | Lower `TEMPERATURE`, strengthen system prompt constraints |
| Pipeline fails on `ai_parse_document` | Ensure pipeline channel is set to `Preview` |
| Vector index not updating | Trigger a sync manually or check pipeline ran successfully |
| Streamlit app auth errors | Verify `app.yaml` resources grant `CAN_QUERY` on the endpoint |
| Stale answers after doc update | Pipeline auto-runs on file arrival; verify job is unpaused |

---

## Future Improvements

- [ ] Add multi-modal retrieval (page images for diagrams/charts)
- [ ] Implement conversation memory for multi-turn interactions
- [ ] Add user feedback collection via the Streamlit app
- [ ] Fine-tune embedding model on domain-specific terminology
- [ ] Add metadata filtering (filter by project, document type)
- [ ] Implement guardrails for PII detection in responses
- [ ] Add A/B testing for different prompt strategies
- [ ] Build a monitoring dashboard for query patterns and quality drift

---

## License

Internal use only. Contains proprietary project documentation.

---

*Built with Databricks AI — Lakeflow Pipelines, AI Search, Model Serving, MLflow, and Databricks Apps.*
