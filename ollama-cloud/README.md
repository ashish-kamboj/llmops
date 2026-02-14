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
   - Open `ollama_cloud_test_notebook.ipynb` in Jupyter/VSCode
   - Run cells in order (from top to bottom)
   - Each cell demonstrates a specific capability

---

## Features & Capabilities

### 1. Chat & Conversation
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