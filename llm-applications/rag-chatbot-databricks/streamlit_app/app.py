"""
RAG Chatbot - Streamlit Application
====================================
A chat interface for querying project documentation using the RAG endpoint.

This app:
- Provides a conversational chat interface
- Calls the Databricks Model Serving RAG endpoint
- Displays answers with source attribution
- Maintains conversation history within a session

Deployment: Databricks Apps
"""

import os
import json
import streamlit as st
import requests
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

# The Model Serving endpoint name (set via app.yaml environment variable)
SERVING_ENDPOINT = os.environ.get("SERVING_ENDPOINT", "rag_project_docs_endpoint")

# Databricks workspace URL and token (automatically available in Databricks Apps)
DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")


# =============================================================================
# API CLIENT
# =============================================================================

def query_rag_endpoint(question: str) -> dict:
    """
    Query the RAG Model Serving endpoint.
    
    Args:
        question: User's question string
        
    Returns:
        dict with 'answer' and optional 'error' keys
    """
    url = f"{DATABRICKS_HOST}/serving-endpoints/{SERVING_ENDPOINT}/invocations"
    
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": [question]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the answer from the response
        if "predictions" in result:
            answer = result["predictions"][0] if isinstance(result["predictions"], list) else result["predictions"]
        elif "outputs" in result:
            answer = result["outputs"][0] if isinstance(result["outputs"], list) else result["outputs"]
        else:
            answer = str(result)
            
        return {"answer": answer}
        
    except requests.exceptions.Timeout:
        return {"answer": None, "error": "Request timed out. Please try again."}
    except requests.exceptions.HTTPError as e:
        return {"answer": None, "error": f"API error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"answer": None, "error": f"Unexpected error: {str(e)}"}


# =============================================================================
# STREAMLIT UI
# =============================================================================

# Page configuration
st.set_page_config(
    page_title="Project Docs Q&A",
    page_icon="📚",
    layout="wide"
)

# Header
st.title("📚 Project Documentation Q&A")
st.markdown(
    "Ask questions about project documentation. "
    "Powered by RAG with Databricks AI."
)

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This chatbot answers questions about project documentation using:
    - **Databricks AI Search** for document retrieval
    - **Claude Haiku 4.5** for answer generation
    - **MLflow** for tracing & observability
    
    ---
    **Tips:**
    - Ask specific questions about project architectures
    - Reference specific pipeline names for targeted answers
    - Ask about processes, flows, or technical details
    """)
    
    st.markdown("---")
    st.markdown(f"**Endpoint:** `{SERVING_ENDPOINT}`")
    st.markdown(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("Ask a question about project documentation..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get response from RAG endpoint
    with st.chat_message("assistant"):
        with st.spinner("Searching documentation..."):
            result = query_rag_endpoint(user_input)
        
        if result.get("error"):
            error_msg = f"⚠️ {result['error']}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            answer = result["answer"]
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
