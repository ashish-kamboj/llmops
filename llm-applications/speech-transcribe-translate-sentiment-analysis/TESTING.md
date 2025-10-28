# Testing Guide for AI Speech Analyzer

## 🧪 Testing Overview

This guide helps you test all features of the AI Speech Analyzer application.

## Test Preparation

### 1. Create Test Audio Files

#### Option A: Record Test Audio
Use any recording software to create short audio clips:

**Test Case 1: Positive Sentiment**
- Record: "I absolutely love this product! It's amazing and exceeded all my expectations. Best purchase ever!"
- Save as: `test_positive.mp3`
- Expected: Positive sentiment

**Test Case 2: Negative Sentiment**
- Record: "This is terrible. I'm very disappointed with the quality. Would not recommend at all."
- Save as: `test_negative.mp3`
- Expected: Negative sentiment

**Test Case 3: Neutral Sentiment**
- Record: "The product arrived on time. It has standard features. The color is blue."
- Save as: `test_neutral.mp3`
- Expected: Neutral sentiment

#### Option B: Use Online Test Audio
Download sample audio from:
- https://www.soundhelix.com/examples (Creative Commons music)
- https://freesound.org/ (Free sound effects)

### 2. Verify Environment Setup

```bash
# Check Python version
python --version  # Should be 3.8+

# Verify virtual environment
pip list | findstr streamlit  # Windows
pip list | grep streamlit     # Linux/Mac

# Test Groq API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', 'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET')"
```

## Manual Testing Checklist

### ✅ Configuration Tests

- [ ] Application loads without errors
- [ ] Config.yaml is read successfully
- [ ] .env file loads API key (always from .env, no sidebar input)
- [ ] Sidebar displays configuration options
- [ ] Model selection dropdown works (llama-3.3-70b-versatile as default)
- [ ] Parallel processing toggle works
- [ ] Visual indicator shows current mode (⚡ Parallel or 🐢 Sequential)

### ✅ File Upload Tests

#### Valid File Tests
- [ ] Upload MP3 file (< 25MB)
- [ ] Upload WAV file
- [ ] Upload M4A file
- [ ] Upload WebM file
- [ ] File info displays correctly
- [ ] Audio player appears and works

#### Invalid File Tests
- [ ] Upload file > 25MB (should show error)
- [ ] Upload unsupported format (.txt, .pdf) (should show error)
- [ ] Upload corrupted audio file (should show error)

### ✅ Processing Tests

#### Speech-to-Text
- [ ] Clear speech transcribes accurately
- [ ] Background noise handling
- [ ] Multiple speakers
- [ ] Different accents
- [ ] Short audio (< 5 seconds)
- [ ] Long audio (> 1 minute)

#### Sentiment Analysis
- [ ] Positive sentiment detected correctly
- [ ] Negative sentiment detected correctly
- [ ] Neutral sentiment detected correctly
- [ ] Mixed sentiment handling
- [ ] Confidence explanation provided
- [ ] Key phrases extracted

#### Translation
- [ ] English to Hindi translation
- [ ] Devanagari script rendering
- [ ] Punctuation preserved
- [ ] Numbers translated appropriately
- [ ] Technical terms handled

### ✅ UI/UX Tests

#### Visual Tests
- [ ] Header gradient displays correctly
- [ ] Cards have proper styling
- [ ] Sentiment badge shows correct color
- [ ] Hindi text renders properly
- [ ] Hover effects work
- [ ] Responsive on different screen sizes
- [ ] Audio recording widget (st.audio_input) displays correctly

#### Interaction Tests
- [ ] Buttons respond to clicks
- [ ] File uploader accepts drag-and-drop
- [ ] Audio recording button works (Streamlit 1.50.0 native widget)
- [ ] Progress bar updates during processing
- [ ] Download button works
- [ ] Sidebar expands/collapses

### ✅ Performance Tests

- [ ] Processing time < 10 seconds for 30-second audio
- [ ] Parallel mode shows correct progress message ("Steps 2-3/3: parallel")
- [ ] Sequential mode shows individual steps (Step 2/3, then Step 3/3)
- [ ] Compare processing times between parallel and sequential modes
- [ ] Logs show detailed timing for each operation
- [ ] Multiple consecutive requests work
- [ ] Memory usage stays reasonable
- [ ] Temp files cleaned up after processing

### ✅ Error Handling Tests

- [ ] Invalid API key shows helpful error
- [ ] Network error displays user-friendly message
- [ ] File validation errors are clear
- [ ] API rate limit handled gracefully
- [ ] Empty audio file handled
- [ ] Corrupted file handled

## Automated Testing Scripts

### Test 1: Configuration Validation

```python
# test_config.py
import yaml
from utils import load_config, load_environment

def test_config_loading():
    try:
        config = load_config("config.yaml")
        assert 'models' in config
        assert 'api' in config
        print("✅ Config loading: PASS")
    except Exception as e:
        print(f"❌ Config loading: FAIL - {e}")

def test_env_loading():
    try:
        api_key = load_environment()
        assert len(api_key) > 0
        print("✅ Environment loading: PASS")
    except Exception as e:
        print(f"❌ Environment loading: FAIL - {e}")

if __name__ == "__main__":
    test_config_loading()
    test_env_loading()
```

Run: `python test_config.py`

### Test 2: Audio Validation

```python
# test_audio_validation.py
from utils import validate_audio_file, load_config

def test_audio_validation():
    config = load_config("config.yaml")
    
    # Test valid file
    is_valid, error = validate_audio_file("test_audio.mp3", config)
    print(f"Valid file test: {'✅ PASS' if is_valid else f'❌ FAIL - {error}'}")
    
    # Test invalid file
    is_valid, error = validate_audio_file("nonexistent.mp3", config)
    print(f"Invalid file test: {'✅ PASS' if not is_valid else '❌ FAIL'}")

if __name__ == "__main__":
    test_audio_validation()
```

Run: `python test_audio_validation.py`

### Test 3: Service Integration

```python
# test_service.py
import asyncio
from services import SpeechAnalysisService
from utils import load_environment, load_config

async def test_service():
    try:
        api_key = load_environment()
        config = load_config("config.yaml")
        
        service = SpeechAnalysisService(api_key, config)
        
        # Test with a real audio file
        results = await service.process_audio_file("test_audio.mp3")
        
        print("✅ Service test: PASS")
        print(f"   Transcription: {results.transcription[:50]}...")
        print(f"   Sentiment: {results.sentiment.sentiment}")
        print(f"   Translation: {results.translation.translated_text[:50]}...")
        print(f"   Time: {results.processing_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Service test: FAIL - {e}")

if __name__ == "__main__":
    asyncio.run(test_service())
```

Run: `python test_service.py`

## Performance Benchmarking

### Benchmark Script

```python
# benchmark.py
import time
import asyncio
from services import SpeechAnalysisService
from utils import load_environment, load_config

async def benchmark():
    api_key = load_environment()
    config = load_config("config.yaml")
    
    # Test parallel vs sequential
    test_files = ["test1.mp3", "test2.mp3", "test3.mp3"]
    
    print("🔄 Running benchmarks...\n")
    
    for mode in [True, False]:
        config['api']['parallel_processing'] = mode
        service = SpeechAnalysisService(api_key, config)
        
        times = []
        for test_file in test_files:
            start = time.time()
            await service.process_audio_file(test_file)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        mode_name = "Parallel" if mode else "Sequential"
        
        print(f"{mode_name} Mode:")
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Min: {min(times):.2f}s")
        print(f"  Max: {max(times):.2f}s")
        print()

if __name__ == "__main__":
    asyncio.run(benchmark())
```

Run: `python benchmark.py`

## Load Testing

### Simple Load Test

```python
# load_test.py
import asyncio
import time
from services import SpeechAnalysisService
from utils import load_environment, load_config

async def process_audio(service, file_path, request_id):
    start = time.time()
    try:
        await service.process_audio_file(file_path)
        elapsed = time.time() - start
        print(f"✅ Request {request_id}: {elapsed:.2f}s")
        return True
    except Exception as e:
        print(f"❌ Request {request_id}: {e}")
        return False

async def load_test(num_requests=5):
    api_key = load_environment()
    config = load_config("config.yaml")
    service = SpeechAnalysisService(api_key, config)
    
    print(f"🔄 Simulating {num_requests} concurrent requests...\n")
    
    tasks = [
        process_audio(service, "test_audio.mp3", i+1)
        for i in range(num_requests)
    ]
    
    start = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start
    
    success_rate = sum(results) / len(results) * 100
    
    print(f"\n📊 Results:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Success rate: {success_rate:.1f}%")
    print(f"  Average per request: {total_time/num_requests:.2f}s")

if __name__ == "__main__":
    asyncio.run(load_test(5))
```

Run: `python load_test.py`

## Common Test Scenarios

### Scenario 1: End-to-End Happy Path

1. Start application: `streamlit run app.py`
2. Ensure API key is in .env file
3. Upload `test_positive.mp3` or record audio using st.audio_input
4. Click "Analyze Speech" or "Analyze Recorded Speech"
5. Verify:
   - Transcription is accurate
   - Sentiment is "Positive"
   - Hindi translation is present
   - Processing time < 10s
   - Download button works

### Scenario 2: Error Recovery

1. Start application
2. Delete or rename .env file (to test missing API key)
3. Verify error message is helpful
4. Restore .env file with API key
5. Restart or refresh the app
6. Verify it works

### Scenario 3: Multiple Files

1. Analyze first file
2. Upload second file
3. Analyze second file
4. Verify results update correctly
5. Check temp files cleaned up

### Scenario 4: Configuration Changes

1. Analyze with default models (parallel mode ON)
2. Note the processing time
3. Toggle parallel processing OFF
4. Analyze same file in sequential mode
5. Compare processing times (check logs for detailed breakdown)
6. Change to faster model (llama-3.1-8b-instant)
7. Verify faster processing time
8. Change to turbo Whisper model
9. Verify even faster processing

## Test Results Template

```
═══════════════════════════════════════════════════
           AI Speech Analyzer Test Report
═══════════════════════════════════════════════════

Date: ________________
Tester: ______________
Version: _____________

Configuration Tests:           [PASS / FAIL]
File Upload Tests:             [PASS / FAIL]
Speech-to-Text Tests:          [PASS / FAIL]
Sentiment Analysis Tests:      [PASS / FAIL]
Translation Tests:             [PASS / FAIL]
UI/UX Tests:                   [PASS / FAIL]
Performance Tests:             [PASS / FAIL]
Error Handling Tests:          [PASS / FAIL]

Overall Status:                [PASS / FAIL]

Notes:
_________________________________________________
_________________________________________________
_________________________________________________

Issues Found:
_________________________________________________
_________________________________________________
_________________________________________________
```

## Debugging Tips

### Enable Debug Logging

Edit `config.yaml`:
```yaml
logging:
  level: "DEBUG"
  enable_file_logging: true
  log_file: "logs/app.log"
```

### View Logs in Real-Time

```powershell
# Windows PowerShell
Get-Content logs/app.log -Wait

# Or open in VS Code
code logs/app.log
```

### Common Issues & Solutions

**Issue**: "No module named 'groq'"
**Solution**: `pip install -r requirements.txt`

**Issue**: Slow processing
**Solution**: Enable parallel processing in config

**Issue**: Translation not in Hindi
**Solution**: Check Llama model version, upgrade if needed

**Issue**: Audio player not working
**Solution**: Convert audio to MP3 format

## Continuous Testing

Add these tests to your CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Test AI Speech Analyzer

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python test_config.py
      - run: python test_audio_validation.py
      # Add more tests
```

---

**Happy Testing! 🧪**

For issues or questions, check the main README.md or open an issue.
