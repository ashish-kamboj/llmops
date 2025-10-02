
# Table of Contents

- [ollama_llm_run.py](#ollama_llm_runpy)
- [ollama_chat_mlflow_app.py](#ollama_chat_mlflow_apppy)

## ollama_llm_run.py

**Ollama LLM Client with Persistent Response Caching:** This code provides a simple Python interface to interact with the **Ollama** LLM API, featuring built-in persistent caching for improved efficiency and repeated query performance.

**Key Features:**
- **Response Caching:** Automatically caches responses for repeated prompts, reducing API calls and speeding up results.
- **Persistent Cache:** Cache is stored on disk (`ollama_cache.pkl`) and persists across program runs.
- **Performance Metrics:** Measures and logs response times for both API calls and cache retrievals.
- **Cache Management:** Utilities to load, save, clear, and inspect cache statistics.
- **Demo Functionality:** Includes a ready-to-run demo (`demo_caching()`) that demonstrates cache usage and speed improvements.

**Usage:**
- Call `get_response(prompt, model, use_cache=True)` to fetch results from the Ollama API with optional caching.
- Run the script directly (`python ollama_llm_run.py`) to see a demonstration of the caching behavior and performance benefits.

**Configuration:**
- **OLLAMA_BASE_URL:** Set to your Ollama instance (default: `http://localhost:11434/api/generate`).
- **DEFAULT_MODEL:** Default model used for queries (e.g., `"llama3"`).
- **CACHE_FILE:** Path to the persistent cache file.

**Example:**
```python
from ollama_llm_run import get_response

response, elapsed = get_response("What is the capital of India?", model="llama3")
print(f"Response: {response} (Time: {elapsed:.2f}s)")
```

---

This module is ideal for scenarios where repeated LLM queries are expected and efficiency is crucial. It is also useful for experimenting with Ollama locally and benchmarking response times.

## ollama_chat_mlflow_app.py

This code provides a Streamlit-based chat application that interfaces with a local Ollama server using its OpenAI-compatible API. The app is enhanced with MLflow GenAI tracing, allowing you to monitor and analyze token usage and conversation traces for each interaction with the LLM.

**Key Features:**
- **Conversational UI:** Uses Streamlit's chat components to collect and display messages in a user-friendly conversational interface.
- **Ollama Integration:** Sends the entire conversation history to an Ollama-hosted model via the OpenAI Python SDK, leveraging Ollama's OpenAI-compatible REST API.
- **MLflow GenAI Tracing:** Automatically tracks and logs LLM interactions, including input, output, and total token usage, using `mlflow.openai.autolog()`. Each interaction's token usage is persisted as MLflow metrics for easy analysis and visualization.
- **Token Usage Insights:** Surfaces detailed token usage statistics per interaction in the Streamlit sidebar, including per-span details for transparency.
- **Customizable Model Selection:** Easily switch between different Ollama models by specifying the model name in the sidebar settings.

**How It Works:**
1. **Session Management:** Maintains chat history and token usage summaries using Streamlit's session state.
2. **Tracing & Logging:** After each user prompt and model response, the app retrieves the latest MLflow trace and logs token usage for comprehensive experiment tracking.
3. **Interactive Sidebar:** Displays current and historical token usage, allowing users to monitor resource consumption over time.

This setup is ideal for those wanting to run local LLMs with experiment tracking and transparent usage analytics, all within an intuitive web interface.

---