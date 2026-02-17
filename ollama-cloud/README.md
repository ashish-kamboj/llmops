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

### 3. Thinking/Reasoning
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

### 4. Vision
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