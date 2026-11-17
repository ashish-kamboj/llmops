# Architecture Documentation

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (Streamlit Web App)                           │
│  ┌───────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ File Upload   │  │ Configuration│  │  Results Display   │   │
│  │   Widget      │  │   Sidebar    │  │   (Beautiful UI)   │   │
│  └───────────────┘  └──────────────┘  └────────────────────┘   │
│  ┌───────────────┐                                        │   │
│  │ Audio Recorder│                                        │   │
│  │   Widget      │                                        │   │
│  └───────────────┘                                        │   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Streamlit Events
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Logic                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Session Management | Config Loader | File Validator       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Service Layer (services.py)                  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            SpeechAnalysisService                          │   │
│  │                                                           │   │
│  │  Step 1:                                                  │   │
│  │  ┌─────────────────────────────────────┐                 │   │
│  │  │   Speech-to-Text (Whisper)          │                 │   │
│  │  │   • Synchronous operation           │                 │   │
│  │  │   • Converts audio → text           │                 │   │
│  │  └─────────────────────────────────────┘                 │   │
│  │                    │                                      │   │
│  │                    ▼                                      │   │
│  │  Step 2 & 3 (PARALLEL):                                  │   │
│  │  ┌──────────────────────┐  ┌──────────────────────┐     │   │
│  │  │ Sentiment Analysis   │  │  Translation         │     │   │
│  │  │ • Async operation    │  │  • Async operation   │     │   │
│  │  │ • Uses Llama LLM     │  │  • Uses Llama LLM    │     │   │
│  │  │ • Classifies emotion │  │  • English → Hindi   │     │   │
│  │  └──────────────────────┘  └──────────────────────┘     │   │
│  │                    │                    │                 │   │
│  │                    └────────┬───────────┘                │   │
│  │                             │                             │   │
│  │                    asyncio.gather()                       │   │
│  │              (Parallel Execution)                         │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Groq API Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Whisper    │  │   Llama 3.1  │  │    Llama 3.1         │  │
│  │   API Call   │  │  API Call    │  │    API Call          │  │
│  │ (STT Model)  │  │ (Sentiment)  │  │   (Translation)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
[User] 
  │
  │ 1. Uploads audio file or records audio
  ▼
[Streamlit UI]
  │
  │ 2. Saves to temp directory
  ▼
[File Validator]
  │
  │ 3. Validates format, size
  ▼
[SpeechAnalysisService]
  │
  │ 4. Reads audio file
  ▼
[Groq Whisper API] ────────────────┐
  │                                 │
  │ 5. Returns transcription        │ Sequential
  ▼                                 │ Operation
[Async Orchestrator]                │
  │                                 │
  ├─────────────────┬───────────────┘
  │                 │
  │                 │ 6. Parallel execution starts
  ▼                 ▼
[Sentiment Task]  [Translation Task]
  │                 │
  │ 7a. Analyze     │ 7b. Translate
  │    with Llama   │     with Llama
  ▼                 ▼
[Groq LLM API]    [Groq LLM API]
  │                 │
  │ 8a. Returns     │ 8b. Returns
  │    sentiment    │     Hindi text
  │                 │
  └────────┬────────┘
           │
           │ 9. asyncio.gather() combines results
           ▼
    [Combined Results]
           │
           │ 10. Format and display
           ▼
    [Beautiful UI Display]
           │
           │ 11. User views results
           ▼
         [User]
```

## Component Interaction Sequence

```
User          Streamlit      Utils          Services        Groq API
 │               │             │               │               │
 │ Upload File   │             │               │               │
 ├──────────────>│             │               │               │
 │               │             │               │               │
 │               │ Validate    │               │               │
 │               ├────────────>│               │               │
 │               │             │               │               │
 │               │<────────────┤               │               │
 │               │  Valid ✓    │               │               │
 │               │             │               │               │
 │ Click Analyze │             │               │               │
 ├──────────────>│             │               │               │
 │               │             │               │               │
 │               │ Initialize Service         │               │
 │               ├────────────────────────────>│               │
 │               │             │               │               │
 │               │             │ process_audio_file()          │
 │               │             │               ├──────────────>│
 │               │             │               │  Whisper STT  │
 │               │             │               │<──────────────│
 │               │             │               │  Transcription│
 │               │             │               │               │
 │               │             │ analyze_sentiment() (async)   │
 │               │             │               ├──────────────>│
 │               │             │               │  Llama Prompt │
 │               │             │               │               │
 │               │             │ translate_to_hindi() (async)  │
 │               │             │               ├──────────────>│
 │               │             │               │  Llama Prompt │
 │               │             │               │               │
 │               │             │               │<──────────────│
 │               │             │               │  Sentiment ✓  │
 │               │             │               │<──────────────│
 │               │             │               │  Translation ✓│
 │               │             │               │               │
 │               │<────────────────────────────│               │
 │               │      Combined Results       │               │
 │               │             │               │               │
 │<──────────────┤             │               │               │
 │  Display      │             │               │               │
 │  Results      │             │               │               │
```

## API Communication Pattern

### Why REST API (Not WebSockets)?

```
REST API (Used)                    WebSockets (Not Used)
─────────────────────────────────  ────────────────────────────────
✓ Stateless operations             ✗ Maintains persistent connection
✓ Simple request/response          ✗ Complex bidirectional channel
✓ Easy to cache                    ✗ Not cacheable
✓ Horizontally scalable            ✗ Requires sticky sessions
✓ Standard HTTP infrastructure     ✗ Special proxy configuration
✓ Perfect for independent tasks    ✗ Overkill for our use case

Our Use Case:
• Speech-to-text: One-time conversion
• Sentiment: Independent analysis
• Translation: Independent task
→ REST API is the right choice!
```

## Parallel Processing Architecture

```
                    Transcribed Text
                          │
                          ▼
              ┌───────────────────────┐
              │  Should we parallelize?│
              └───────────────────────┘
                          │
          ┌───────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
    Sequential Mode                   Parallel Mode
  (config: false)                    (config: true)
          │                                 │
          ▼                                 ▼
    ┌─────────┐                      ┌─────────┐
    │Sentiment│                      │ async   │
    │Analysis │                      │ Task 1: │
    │ 2-3 sec │                      │Sentiment│
    └────┬────┘                      └────┬────┘
         │                                 │
         ▼                                 │
    ┌─────────┐                           │
    │Translate│                      ┌────┴────┐
    │ 2-4 sec │                      │ async   │
    └────┬────┘                      │ Task 2: │
         │                           │Translate│
         ▼                           └────┬────┘
    Total: 6-8s                           │
                                          ▼
                              asyncio.gather(task1, task2)
                                          │
                                          ▼
                                     Total: 3-5s
                                   (50% faster!)
```

## Module Responsibilities

### app.py (UI Layer)
- Render Streamlit interface
- Handle user interactions (file upload, audio recording)
- Display results beautifully
- Manage session state
- Load custom CSS
- Support both file upload and audio recording (st.audio_input)
- Toggle between parallel and sequential processing modes

### services.py (Business Logic)
- `SpeechAnalysisService` class
- Speech-to-text conversion (synchronous, required by Groq SDK)
- Sentiment analysis (async)
- Translation (async)
- Async orchestration with parallel/sequential mode toggle
- API communication with detailed timing logs
- Configurable processing modes for performance vs debugging

### utils.py (Helper Functions)
- Load configuration (YAML)
- Load environment variables (Groq API key always from .env)
- Validate audio files
- File operations
- Formatting helpers
- Logging setup

### config.yaml (Configuration)
- Model selection
- API settings
- Audio constraints
- UI customization
- Feature flags

## Error Handling Flow

```
[API Call]
    │
    ├─ Success? ──> [Parse Response] ──> [Return Result]
    │
    └─ Failure?
        │
        ├─ Network Error ────> [Retry Logic] ──> [Log & Report]
        │                            │
        │                            └─> Max retries exceeded?
        │                                     │
        │                                     └─> [User-friendly error]
        │
        ├─ Authentication Error ──> [Check API key] ──> [Show help]
        │
        ├─ Rate Limit ───────────> [Wait & Retry] ──> [Log]
        │
        └─ Invalid Response ─────> [Log details] ──> [Show error]
```

## Configuration Management

```
[Application Start]
  │
  ├──> Load config.yaml
  │       │
  │       ├─ Parse YAML
  │       ├─ Validate schema
  │       └─ Set defaults
  │
  ├──> Load .env file
  │       │
  │       ├─ Read API key (always from .env)
  │       └─ Optional settings
  │
  └──> Initialize services
    │
    ├─ SpeechAnalysisService(config)
    └─ Ready for requests
```

## Why No AI Agents?

```
AI Agent Frameworks          Direct API Calls
(CrewAI, LangGraph)         (Our Approach)
─────────────────────────   ───────────────────────
✗ Autonomous decisions      ✓ Explicit control
✗ Complex workflows         ✓ Simple linear flow
✗ Agent communication       ✓ Direct function calls
✗ Higher latency            ✓ Minimal overhead
✗ Harder to debug           ✓ Easy to trace
✗ Overkill for simple ops   ✓ Right-sized solution

When to use Agents:
• Multi-step reasoning
• Dynamic tool selection
• Iterative refinement
• Complex decision trees

Our Use Case:
• Fixed 3-step pipeline
• Predetermined tasks
• No decision-making needed
→ Direct APIs are better!
```

## Scalability Considerations

### Current Implementation
- Single-threaded Streamlit app
- One request at a time per user
- Groq API handles concurrency

### Production Scaling Options

```
Option 1: Horizontal Scaling
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Streamlit   │  │ Streamlit   │  │ Streamlit   │
│ Instance 1  │  │ Instance 2  │  │ Instance 3  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┴────────────────┘
                       │
              ┌────────┴────────┐
              │ Load Balancer   │
              └─────────────────┘

Option 2: Queue-Based Processing
[Streamlit] → [Message Queue] → [Worker Pool] → [Groq API]
   (UI)          (Redis/RabbitMQ)   (Multiple)     (Cloud)

Option 3: Microservices
[UI Service] → [STT Service] → [Analysis Service] → [Results]
  (Port 8501)    (Port 8001)       (Port 8002)      (Storage)
```

## Performance Monitoring Points

```
┌─────────────┐
│ User Upload │
└──────┬──────┘
       │ ⏱️ Upload Time
       ▼
┌─────────────┐
│ Validation  │
└──────┬──────┘
       │ ⏱️ Validation Time
       ▼
┌─────────────┐
│ STT API     │
└──────┬──────┘
       │ ⏱️ Transcription Time
       ▼
┌─────────────┐
│ Parallel    │
│ Processing  │
└──────┬──────┘
       │ ⏱️ Analysis Time
       ▼
┌─────────────┐
│ Display     │
└──────┬──────┘
       │ ⏱️ Total Processing Time
       ▼
    [Results]

Metrics to track:
• Average processing time
• API response times
• Error rates
• File sizes
• Concurrent users
```

## Security Architecture

```
[User] ──(HTTPS)──> [Streamlit App]
                          │
                    ┌─────┴─────┐
                    │           │
              File Upload     API Key
                    │           │
              ┌─────┴─────┐    │
              │ Validate  │    │
              │ • Size    │    │
              │ • Format  │    │
              │ • Content │    │
              └─────┬─────┘    │
                    │           │
              [Temp Storage]   [Environment]
                    │           │
                    └─────┬─────┘
                          │
                    [Groq API]
                          │
                    ┌─────┴─────┐
                    │ TLS 1.3   │
                    │ Encrypted │
                    └───────────┘
```

---

**Key Takeaways:**

1. **REST API** for simplicity and scalability
2. **Async/Parallel** for performance optimization
3. **No AI Agents** - direct APIs are more efficient
4. **Modular Design** - easy to extend and maintain
5. **Production-Ready** - error handling, validation, logging
