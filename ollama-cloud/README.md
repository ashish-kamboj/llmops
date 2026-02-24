# Ollama Cloud Testing & Capabilities Showcase

Comprehensive guide and testing suite for Ollama Cloud API with samples for all major capabilities.

## Table of Contents

- [What is Ollama?](#what-is-ollama)
- [Getting Started](#getting-started)
- [Features & Capabilities](#features--capabilities)
- [Setup Instructions](#setup-instructions)
- [Running the Tests](#running-the-tests)
- [API Key Configuration](#api-key-configuration)
- [Model Selection Guide](#model-selection-guide)
- [Code Examples](#code-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## What is Ollama?

**Ollama** is an open-source framework that makes running, creating, and sharing large language models accessible and practical. Unlike traditional cloud AI services, Ollama enables:

### Key Innovations
- **No GPU Required**: Run powerful models (120B parameters) without local GPU hardware
- **Cloud-Native Architecture**: Models automatically offload to Ollama's cloud infrastructure
- **Same API Interface**: Identical API for local and cloud models
- **Full Context Windows**: Cloud models run at their full context length (32K+ tokens)
- **Open Models**: Access to cutting-edge open-source models

### Why Use Ollama Cloud?

| Feature | Local Ollama | Ollama Cloud |
|---------|-------------|--------------|
| **GPU Requirements** | Yes, needed for large models | No, runs in cloud |
| **Model Size** | Limited by local hardware | Run 120B+ models easily |
| **Cost** | Hardware investment + electricity | Pay-per-token pricing |
| **Scaling** | Manual infrastructure | Automatic scaling |
| **Latest Models** | Requires updates | Always latest versions |
| **Development** | Great for prototyping | Best for production |

---

## Getting Started

### Prerequisites

1. **Ollama Account** - Create at [ollama.com](https://ollama.com)
2. **API Key** - Generate from [ollama.com/settings/keys](https://ollama.com/settings/keys)
3. **Python 3.8+** - For running the notebook
4. **Internet Connection** - For cloud API access

### Quick Start

1. **Clone/Download the notebook**
   ```bash
   cd ollama-cloud
   ```

2. **Install dependencies**
   ```bash
   pip install ollama python-dotenv requests
   ```

3. **Configure API key**
   - Edit `.env` file in this directory
   - Add your API key: `OLLAMA_API_KEY=your_key_here`
   - Get it from: https://ollama.com/settings/keys

4. **Run the notebook**
   - Open the specific notebook in Jupyter/VSCode
   - Run cells in order (from top to bottom)
   - Each cell demonstrates a specific capability

---

## Features & Capabilities

### 1. Chat & Conversation - `1_ollama_chat.ipynb`
**Basic conversational AI**
- Simple question-answer interactions
- Multi-turn conversations
- Context awareness

```python
response = client.chat(
    model='gpt-oss:120b',
    messages=[{'role': 'user', 'content': 'What is AI?'}],
    stream=False
)
```

### 2. Streaming - `2_ollama_streaming.ipynb`
**Real-time token streaming**
- Lower latency perception
- Better UX for long responses
- Live output display

```python
stream = client.chat(
    model='qwen3-next:80b',
    messages=[{'role': 'user', 'content': 'Write a poem'}],
    stream=True
)
for chunk in stream:
    print(chunk.message.content, end='', flush=True)
```

### 3. Thinking/Reasoning - `3_ollama_thinking.ipynb`
**Extended reasoning with transparent thought process**
- Models show their reasoning
- Ideal for complex problems
- Better auditability

**Supported Models**: Qwen3-next, DeepSeek R1, GPT-OSS:120b

```python
response = client.chat(
    model='qwen3-next:80b',
    messages=[{'role': 'user', 'content': 'Solve this math problem...'}],
    think=True,
    stream=True
)
# Access response.message.thinking for reasoning trace
# Access response.message.content for final answer
```

### 4. Vision - `4_ollama_vision.ipynb`
**Image understanding and analysis**
- Describe images
- Answer questions about images
- Document analysis
- Scene understanding

**Supported Models**: Qwen3-vl, Gemma3, Mistral-3, devstral-small-2

**Important**: Images must be provided as base64-encoded strings, not URLs. Download images and encode them first.

```python
import base64
import requests

# Download and encode image
response_img = requests.get('https://example.com/image.jpg')
image_data = base64.b64encode(response_img.content).decode('utf-8')

# Send to model
response = client.chat(
    model='gemma3:4b',
    messages=[{
        'role': 'user',
        'content': 'Describe this image',
        'images': [image_data]  # Pass base64 string
    }]
)
```

### 5. Tool Calling - `5_ollama_tool_calling.ipynb`
**Extend models with custom functions**
- Models decide when to use tools
- Function calling and execution
- Complex workflows

**Supported Models**: Qwen3-next, GPT-OSS:120b, DeepSeek-v3.1

```python
response = client.chat(
    model='gpt-oss:120b',
    messages=[{'role': 'user', 'content': 'Calculate 17 × 23'}],
    tools=[tool_definitions],
    stream=False
)
# Check response.message.tool_calls for function requests
```

### 6. Web Search - `6_ollama_web_search.ipynb`
**Real-time web information access**
- Search the internet
- Fetch web pages
- Reduce hallucinations
- Current information

```python
results = client.web_search('What is Ollama?', max_results=5)
for result in results.results:
    print(f"{result.title}: {result.url}")
```

### 7. AI Agents with web search capability - `7_ollama_agent_with_web_search.ipynb`
**Combine multiple capabilities for autonomous reasoning**
- Research and fact-finding
- Complex decision-making
- Multi-step workflows

### 8. Embeddings with Vector Search (`8_ollama_embedding.ipynb`)
**How It Works**

1. **Generate Embeddings**: Convert documents into vectors using `mxbai-embed-large` model
2. **Store & Index**: Store embeddings in ChromaDB vector database
3. **Retrieve & Generate**: Query for relevant documents and generate answers using `gemma3:1b`

```python
import ollama
import chromadb

# Step 1: Create vector database and store documents
documents = [
    "Llamas are members of the camelid family...",
    "Llamas were first domesticated 4,000 to 5,000 years ago...",
    # ... more documents
]

client = chromadb.Client()
collection = client.create_collection(name="docs")

# Generate and store embeddings
for i, doc in enumerate(documents):
    response = ollama.embed(model="mxbai-embed-large", input=doc)
    collection.add(
        ids=[str(i)],
        embeddings=response["embeddings"],
        documents=[doc]
    )

# Step 2: Retrieve relevant documents
prompt = "What animals are llamas related to?"
response = ollama.embed(model="mxbai-embed-large", input=prompt)
results = collection.query(
    query_embeddings=response["embeddings"],
    n_results=1
)
retrieved_doc = results['documents'][0][0]

# Step 3: Generate answer with context
output = ollama.generate(
    model="gemma3:1b",
    prompt=f"Using this data: {retrieved_doc}. Respond to: {prompt}"
)
print(output['response'])
```

**Models Used**
- **Embedding Model**: `mxbai-embed-large` - High-quality text embeddings
- **Generation Model**: `gemma3:1b` - Lightweight model for generating responses

---

## Setup Instructions

### 1. Environment Configuration

Create a `.env` file in the `ollama-cloud` directory:

```env
# Required: Your API key
OLLAMA_API_KEY=your_api_key_here

# Optional: API endpoint (defaults to https://ollama.com)
OLLAMA_API_ENDPOINT=https://ollama.com

# Optional: Default model for testing
DEFAULT_MODEL=gpt-oss:120b

# Optional: Logging level
LOG_LEVEL=INFO
```

### 2. Get Your API Key

1. Go to https://ollama.com/settings/keys
2. Click "Create New Key"
3. Copy the key
4. Paste into `.env` file

### 3. Verify Installation

```python
import ollama
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OLLAMA_API_KEY')
print(f"API Key configured: {api_key is not None}")
```

---

## Running the Tests

### In Jupyter Notebook/VSCode

1. For the all-in-one walkthrough, open `ollama_cloud_test_notebook.ipynb`
2. For focused capability demos, open the dedicated notebooks:
    - `1_ollama_chat.ipynb` (Chat)
    - `2_ollama_streaming.ipynb` (Streaming)
    - `3_ollama_thinking.ipynb` (Thinking)
    - `4_ollama_vision.ipynb` (Vision)
    - `5_ollama_tool_calling.ipynb` (Tool Calling)
    - `6_ollama_web_search.ipynb` (Web Search + Web Fetch)
    - `7_ollama_agent_with_web_search.ipynb` (AI Agent)
    - `8_ollama_embedding.ipynb` (Embeddings with Vector Search)
3. Run cells in order:
    - **Cell 1**: Setup (install packages)
    - **Cell 2**: Import libraries and configure
    - **Cells 3+**: Test individual capabilities

### Expected Output

Each test cell will display:
- Success indicators
- Operation details
- Progress updates
- Results and metrics

### Running Individual Tests

```python
# Basic chat
test_basic_chat(prompt="Your question here")

# Streaming
test_streaming_chat()

# Thinking
test_thinking_with_streaming(model='qwen3-next:80b')

# Vision (downloads image, encodes base64)
test_vision_with_url(image_url='https://example.com/image.jpg')

# Tool calling
test_tool_calling(user_query='Calculate something')

# Web search
test_web_search(query='What is AI?')

# Web fetch
test_web_fetch(url='https://example.com')

# AI Agent
test_ai_agent_with_search(query='Research topic X')
```

---

## API Key Configuration

### Security Best Practices

**DO**
- Store API key in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables in production
- Rotate keys periodically
- Use specific API keys per application

**DON'T**
- Commit API keys to version control
- Share keys publicly
- Use the same key everywhere
- Log or print API keys
- Hardcode keys in source code

### Environment Variable Methods

**Python (using python-dotenv)**
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OLLAMA_API_KEY')
```

**System Environment (Linux/Mac)**
```bash
export OLLAMA_API_KEY=your_key_here
```

**System Environment (Windows PowerShell)**
```powershell
$env:OLLAMA_API_KEY = 'your_key_here'
```

---

## Model Selection Guide

### For Reasoning Tasks
**Qwen3** (Recommended for most cases)
- Fast and efficient
- Native thinking support
- Balanced quality/speed
- Tool calling support

```python
client.chat(model='qwen3', ...)
```

**DeepSeek R1**
- Advanced reasoning
- Transparent thinking
- Better for complex problems

```python
client.chat(model='deepseek-r1', ...)
```

**GPT-OSS:120b**
- Most capable
- Extended thinking (low/medium/high)
- Full context length

```python
response = client.chat(
    model='gpt-oss:120b',
    think='medium',  # or 'low', 'high'
    ...
)
```

### For Vision Tasks
**Llama4:scout (109B)** (Recommended)
- Best vision capabilities
- Large context window
- Multimodal understanding

```python
client.chat(model='llama4:scout', ...)
```

**Qwen2.5VL**
- Good balance
- Faster than Llama4:scout
- Strong vision capabilities

```python
client.chat(model='qwen2.5vl', ...)
```

### For Embeddings
**Nomic-embed-text** (Recommended)
- Dimension: 768
- Good quality/speed balance
- General purpose

```python
client.embed(model='nomic-embed-text', ...)
```

**Mxbai-embed-large**
- Dimension: 1024
- Higher quality
- More computational cost

```python
client.embed(model='mxbai-embed-large', ...)
```

### For Speed
**Mistral Small 3.2**
- Fastest model
- Still good quality
- Efficient

```python
client.chat(model='mistral-small:3.2', ...)
```

### Decision Matrix

| Task | Best Model | Why |
|------|-----------|-----|
| General chat | Qwen3 | Fast, capable, balanced |
| Complex reasoning | GPT-OSS:120b | Most capable |
| Quick responses | Mistral Small 3.2 | Fastest |
| Image analysis | Llama4:scout | Best vision |
| Embeddings | Nomic-embed-text | Good balance |
| Tool calling | Qwen3 | Excellent support |
| Web search agent | Qwen3 | Good reasoner, fast |

---

## Code Examples

### Example 1: Simple Chatbot

```python
from ollama import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(
    host="https://ollama.com",
    headers={'Authorization': f'Bearer {os.getenv("OLLAMA_API_KEY")}'}
)

def chatbot():
    messages = []
    print("Chatbot (type 'quit' to exit)\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        
        messages.append({'role': 'user', 'content': user_input})
        
        response = client.chat(
            model='gpt-oss:120b',
            messages=messages,
            stream=False
        )
        
        assistant_message = response.message.content
        messages.append({'role': 'assistant', 'content': assistant_message})
        
        print(f"Assistant: {assistant_message}\n")

chatbot()
```

### Example 2: Image Analysis with Vision

```python
from ollama import Client
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(
    host="https://ollama.com",
    headers={'Authorization': f'Bearer {os.getenv("OLLAMA_API_KEY")}'}
)

def analyze_image(image_url: str, question: str = "Describe this image"):
    """Analyze an image using vision model."""
    response_img = requests.get(image_url, timeout=10)
    response_img.raise_for_status()
    image_data = base64.b64encode(response_img.content).decode('utf-8')

    response = client.chat(
        model='gemma3:4b',
        messages=[{
            'role': 'user',
            'content': question,
            'images': [image_data]
        }],
        stream=False
    )
    
    return response.message.content

# Usage
image_url = "https://example.com/image.jpg"
analysis = analyze_image(image_url, "What objects are in this image?")
print(analysis)
```

### Example 3: Research Agent with Web Search

```python
from ollama import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(
    host="https://ollama.com",
    headers={'Authorization': f'Bearer {os.getenv("OLLAMA_API_KEY")}'}
)

def research_topic(topic: str):
    """Research a topic using web search."""
    
    print(f"Researching: {topic}\n")
    
    # Search
    results = client.web_search(topic, max_results=3)
    
    print("Search Results:")
    sources = []
    for result in results.results:
        print(f"• {result.title}")
        print(f"  {result.url}")
        sources.append(result.content)
    
    # Generate summary using search results
    context = "\n\n".join(sources)
    
    response = client.chat(
        model='gpt-oss:120b',
        messages=[{
            'role': 'user',
            'content': f"Based on these sources, summarize {topic}:\n\n{context}"
        }],
        stream=False
    )
    
    print(f"\nSummary:\n{response.message.content}")

# Usage
research_topic("Latest AI developments 2025")
```

---

## Best Practices

### 1. Error Handling

```python
import logging
from ollama import ResponseError

logging.basicConfig(level=logging.INFO)

try:
    response = client.chat(
        model='qwen3',
        messages=[...],
        stream=False,
        timeout=30
    )
except ResponseError as e:
    logging.error(f"API error: {e}")
except Exception as e:
    logging.error(f"Unexpected error: {e}")
```

### 2. Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_second: float = 1):
    """Decorator to rate limit API calls."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        
        return wrapper
    return decorator

@rate_limit(calls_per_second=2)
def call_api():
    response = client.chat(...)
    return response
```

### 3. Caching

```python
import json
import hashlib
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_embedding(text: str):
    """Cache embeddings to reduce API calls."""
    response = client.embed(
        model='nomic-embed-text',
        input=text
    )
    return response.embeddings[0]

# Or use persistent cache
import pickle
from pathlib import Path

cache_file = Path('embedding_cache.pkl')

def get_embedding_cached(text: str):
    cache = pickle.load(cache_file) if cache_file.exists() else {}
    
    if text not in cache:
        response = client.embed(
            model='nomic-embed-text',
            input=text
        )
        cache[text] = response.embeddings[0]
        
        with open(cache_file, 'wb') as f:
            pickle.dump(cache, f)
    
    return cache[text]
```

### 4. Logging & Monitoring

```python
import logging
import json
from datetime import datetime

logging.basicConfig(
    filename='ollama_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_api_call(model: str, prompt: str, response: str, tokens: int):
    """Log API calls for monitoring."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'model': model,
        'prompt_length': len(prompt),
        'response_length': len(response),
        'tokens_used': tokens
    }
    logging.info(json.dumps(log_entry))
```

---

## Troubleshooting

### Common Issues & Solutions

#### "OLLAMA_API_KEY not set"
```
Problem: API key configuration error
Solution:
1. Verify .env file exists in ollama-cloud directory
2. Check OLLAMA_API_KEY is set correctly
3. Ensure no spaces around = sign
4. Reload environment: load_dotenv(force=True)
```

#### "Model not found"
```
Problem: Model doesn't exist or is misspelled
Solution:
1. Visit https://ollama.com/library
2. Verify exact model name
3. Check model is available in your region
4. Wait for model to load on first run (can take 1-2 minutes)
```

#### "Unauthorized (401)"
```
Problem: Invalid or expired API key
Solution:
1. Check API key at https://ollama.com/settings/keys
2. Generate new key if needed
3. Update .env file
4. Verify no extra spaces or quotes
```

#### "Request timeout"
```
Problem: API request took too long
Solution:
1. Increase timeout value: timeout=60
2. Try with smaller model (faster)
3. Check internet connection
4. Retry with exponential backoff
```

#### "Web search returns empty results"
```
Problem: Web search not working
Solution:
1. Use client.web_search() NOT ollama.web_search()
2. Ensure Bearer token in Authorization header
3. Verify API key has web search permission
4. Try different search query
5. Check internet connection
```

#### "Web search/fetch returns '403 Forbidden' error"
```
Problem: Authorization header missing or invalid
Solution:
1. Verify API key is set in .env file
2. Ensure using client.web_search() / client.web_fetch()
3. Check client has Authorization header with Bearer token
4. Confirm OLLAMA_API_KEY=your_actual_key (not placeholder)
```

#### "Vision model returns 'illegal base64 data' error"
```
Problem: Image format incorrect
Solution:
1. Images must be base64-encoded strings, NOT URLs
2. Download image first: requests.get(image_url)
3. Encode with: base64.b64encode(response.content).decode('utf-8')
4. Pass only the base64 string to 'images' array
5. Do NOT include 'data:image/..;base64,' prefix
```

#### "Vision model can't read image"
```
Problem: Image analysis fails
Solution:
1. Use vision-capable model (gemma3:4b, llama4:scout, qwen2.5vl)
2. Ensure image is base64-encoded
3. Check image format (jpg, png, webp)
4. Ensure image is less than 20MB
5. Verify image was downloaded successfully
6. Try with a reliable image source (github raw, etc)
```

#### "Tool calling not working"
```
Problem: Model doesn't call tools
Solution:
1. Use tool-capable model (qwen3, gpt-oss:120b)
2. Verify tool definition format is correct
3. Check parameter types match schema
4. Ensure model understands tool purpose
5. Add example of tool usage in prompt
```

---

## Additional Resources

### Official Documentation
- **Main Docs**: https://docs.ollama.com
- **Cloud Guide**: https://docs.ollama.com/cloud
- **Streaming**: https://docs.ollama.com/capabilities/streaming
- **Thinking**: https://docs.ollama.com/capabilities/thinking
- **Web Search**: https://docs.ollama.com/capabilities/web-search
- **Tool Calling**: https://docs.ollama.com/capabilities/tool-calling

### SDKs & Tools
- **Python SDK**: https://github.com/ollama/ollama-python
- **JavaScript SDK**: https://github.com/ollama/ollama-js
- **Model Library**: https://ollama.com/library
- **Community**: https://ollama.com/community

### Learn More
- **Blog**: https://ollama.com/blog
- **GitHub**: https://github.com/ollama/ollama
- **Discussions**: https://github.com/ollama/ollama/discussions
- **Issues**: https://github.com/ollama/ollama/issues

---

## Support

If you encounter issues:

1. **Check this README** - Most common issues are documented
2. **Review the notebook** - Code examples might help
3. **Check logs** - Enable logging to debug issues
4. **Visit GitHub Issues**: https://github.com/ollama/ollama/issues
5. **Ask Community**: https://ollama.com/community

---
