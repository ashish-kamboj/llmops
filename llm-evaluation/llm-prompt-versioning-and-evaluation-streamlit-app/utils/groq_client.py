import os
from groq import Groq
from typing import Any


def init_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY in environment variables. Please set it in your .env file.")
    return Groq(api_key=api_key)
