"""
Ollama LLM Client with Response Caching

This module provides a simple interface to interact with Ollama API
with built-in caching functionality for improved performance.

Features:
- Response caching for repeated queries
- Performance timing and metrics
- Cache management utilities
"""

import requests
import json
import time
import hashlib
import pickle
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

OLLAMA_BASE_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"
CACHE_FILE = "ollama_cache.pkl"  # Persistent cache file

# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

# Global cache storage
response_cache = {}


def load_cache():
    """Load cache from disk if it exists."""
    global response_cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'rb') as f:
                response_cache = pickle.load(f)
            print(f"✓ Loaded {len(response_cache)} cached responses from disk")
        except Exception as e:
            print(f"⚠️  Could not load cache file: {e}")
            response_cache = {}
    else:
        print("ℹ️  No existing cache file found, starting fresh")


def save_cache():
    """Save cache to disk."""
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(response_cache, f)
        print(f"✓ Saved {len(response_cache)} responses to cache file")
    except Exception as e:
        print(f"⚠️  Could not save cache file: {e}")


def get_cache_key(prompt: str, model: str) -> str:
    """
    Generate a unique cache key from prompt and model.
    
    Args:
        prompt: The input prompt text
        model: The model name
        
    Returns:
        MD5 hash string to use as cache key
    """
    combined = f"{model}:{prompt}"
    return hashlib.md5(combined.encode()).hexdigest()


def clear_cache():
    """Clear all cached responses from memory and disk."""
    global response_cache
    response_cache.clear()
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    print("✓ Cache cleared from memory and disk")


def get_cache_stats():
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache size, file info, and sample keys
    """
    file_size = 0
    if os.path.exists(CACHE_FILE):
        file_size = os.path.getsize(CACHE_FILE)
    
    return {
        "cache_size": len(response_cache),
        "cache_file_exists": os.path.exists(CACHE_FILE),
        "cache_file_size_bytes": file_size,
        "cached_keys": list(response_cache.keys())[:3]  # Show first 3 keys
    }

# ============================================================================
# MAIN API FUNCTIONS
# ============================================================================

def get_response(prompt: str, model: str = DEFAULT_MODEL, use_cache: bool = True):
    """
    Get response from Ollama API with optional caching.
    
    Args:
        prompt: The text prompt to send to the model
        model: Model name (default: llama3)
        use_cache: Whether to use cached responses (default: True)
        
    Returns:
        Tuple of (response_text, response_time_seconds)
    """
    # Check cache first
    if use_cache:
        cache_key = get_cache_key(prompt, model)
        if cache_key in response_cache:
            # Measure cache retrieval time
            cache_start = time.perf_counter()
            cache_entry = response_cache[cache_key]
            cached_response = cache_entry['response']
            original_time = cache_entry['original_time']
            cache_end = time.perf_counter()
            
            cache_retrieval_time = cache_end - cache_start
            print(f"✓ Cache hit! Retrieved from cache (original: {original_time:.2f}s, "
                  f"cache retrieval: {cache_retrieval_time:.4f}s)")
            return cached_response, cache_retrieval_time
    
    # Prepare API request
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    # Make API call with timing
    start_time = time.perf_counter()
    try:
        resp = requests.post(OLLAMA_BASE_URL, headers=headers, data=json.dumps(payload))
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ API Error: {e}")
        return f"Error: {e}", 0.0
    
    end_time = time.perf_counter()
    response_time = end_time - start_time
    
    # Parse response
    data = resp.json()
    response_text = data.get("response", "No response")
    
    # Cache the result
    if use_cache:
        cache_key = get_cache_key(prompt, model)
        cache_entry = {
            'response': response_text,
            'original_time': response_time,
            'timestamp': time.time(),
            'model': model
        }
        response_cache[cache_key] = cache_entry
        save_cache()  # Save to disk immediately
        print(f"✓ Response cached for future use (took {response_time:.2f}s)")
    
    return response_text, response_time

# ============================================================================
# DEMO AND TESTING
# ============================================================================

def demo_caching():
    """
    Demonstrate the caching functionality with performance comparison.
    """
    print("🚀 OLLAMA PERSISTENT CACHING DEMO")
    print("=" * 50)
    
    # Load existing cache
    load_cache()
    
    # Show cache stats
    stats = get_cache_stats()
    print(f"📊 Cache loaded: {stats['cache_size']} items")
    if stats['cache_file_exists']:
        print(f"📁 Cache file size: {stats['cache_file_size_bytes']} bytes")
    
    # Test prompt
    user_prompt = "Capital of India? Provide one word answer"
    model_name = "llama3.2:3b"
    
    # Test 1: Request (may hit cache from previous runs)
    print(f"\n📡 Request: '{user_prompt}'")
    output1, response_time1 = get_response(user_prompt, model=model_name)
    print(f"Response: {output1}")
    print(f"Response time: {response_time1:.4f} seconds")
    
    # Test 2: Same request (should definitely hit cache now)
    print(f"\n💾 Same request again (should use cache)")
    output2, response_time2 = get_response(user_prompt, model=model_name)
    print(f"Response: {output2}")
    print(f"Response time: {response_time2:.4f} seconds")
    
    # Show final cache stats
    final_stats = get_cache_stats()
    print(f"\n📊 Final cache stats: {final_stats['cache_size']} items")
    
    if response_time1 > response_time2 and response_time2 > 0:
        speedup = response_time1 / response_time2
        print(f"🚀 Speed improvement: {speedup:.0f}x faster with cache!")
    
    print(f"\n� The cache persists between runs!")
    print(f"🔄 Run 'python ollama_llm_run.py' again to see cached results immediately")


if __name__ == '__main__':
    demo_caching()