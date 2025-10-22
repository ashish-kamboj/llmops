from typing import List, Dict, Any
from mlflow.entities import Feedback
from mlflow.genai import scorer
from groq import Groq
import json
import os


def build_default_dataset(config_eval: Dict[str, Any]) -> List[Dict[str, Any]]:
    return config_eval.get("default_dataset", [])


def _get_groq_client() -> Groq:
    """Get Groq client instance."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY in environment variables. Please set it in your .env file.")
    return Groq(api_key=api_key)


@scorer
def concept_coverage(outputs: str, expectations: dict) -> Feedback:
    concepts = set(expectations.get("key_concepts", []))
    if not concepts:
        return Feedback(value=1.0, rationale="No key concepts specified to evaluate - scoring as perfect")

    response_lower = outputs.lower()
    included = {c for c in concepts if c.lower() in response_lower}
    coverage_score = len(included) / len(concepts)
    missing_concepts = concepts - included
    rationale = f"Coverage: {len(included)}/{len(concepts)} concepts included"
    if included:
        rationale += f" - Found: {list(included)}"
    if missing_concepts:
        rationale += f" - Missing: {list(missing_concepts)}"
    return Feedback(value=coverage_score, rationale=rationale)


@scorer
def response_length_check(outputs: str, expectations: dict) -> Feedback:
    word_count = len(outputs.split())
    min_words = 10
    max_words = expectations.get("max_length", 100)
    if word_count < min_words:
        score = word_count / min_words
        rationale = f"Response too short ({word_count} words, minimum {min_words} required)"
    elif word_count > max_words:
        score = max_words / word_count
        rationale = f"Response too long ({word_count} words, maximum {max_words} recommended)"
    else:
        score = 1.0
        rationale = f"Response length optimal ({word_count} words within {min_words}-{max_words} range)"
    return Feedback(value=score, rationale=rationale)


# Custom LLM-based scorers using Groq API
@scorer
def is_concise(outputs: str, expectations: dict) -> Feedback:
    """
    Evaluate if the response is concise and to the point.
    
    This scorer assesses brevity and directness, penalizing unnecessary details
    while rewarding clear, focused responses that get to the point quickly.
    """
    try:
        client = _get_groq_client()
        evaluation_prompt = [
            {"role": "system", "content": "You are an expert evaluator. Rate responses on a scale of 0-1 where 1 is perfect."},
            {"role": "user", "content": f"""
Evaluate this response for conciseness (brevity and directness):

Response: "{outputs}"

Guidelines: The response should be concise and to the point. Avoid unnecessary details.
Score based on how well the response balances completeness with brevity.

Provide your evaluation in this exact JSON format:
{{"score": 0.85, "rationale": "Brief explanation of your score"}}
"""}
        ]
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=evaluation_prompt,
            temperature=0.1,  # Low temperature for consistent evaluation
            max_tokens=200,
        )
        
        result = response.choices[0].message.content
        try:
            eval_result = json.loads(result)
            return Feedback(value=eval_result["score"], rationale=eval_result["rationale"])
        except (json.JSONDecodeError, KeyError):
            return Feedback(value=0.5, rationale=f"Could not parse evaluation: {result}")
            
    except Exception as e:
        return Feedback(value=0.0, rationale=f"Evaluation error: {str(e)}")


@scorer
def is_professional(outputs: str, expectations: dict) -> Feedback:
    """
    Evaluate if the response maintains professional tone.
    
    This scorer assesses whether the response uses appropriate language,
    maintains formality, and presents information in a professional manner.
    """
    try:
        client = _get_groq_client()
        evaluation_prompt = [
            {"role": "system", "content": "You are an expert evaluator. Rate responses on a scale of 0-1 where 1 is perfect."},
            {"role": "user", "content": f"""
Evaluate this response for professional tone:

Response: "{outputs}"

Guidelines: The response should be written in a professional, clear, and appropriate tone.
Consider language choice, formality level, and overall presentation.

Provide your evaluation in this exact JSON format:
{{"score": 0.85, "rationale": "Brief explanation of your score"}}
"""}
        ]
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=evaluation_prompt,
            temperature=0.1,
            max_tokens=200,
        )
        
        result = response.choices[0].message.content
        try:
            eval_result = json.loads(result)
            return Feedback(value=eval_result["score"], rationale=eval_result["rationale"])
        except (json.JSONDecodeError, KeyError):
            return Feedback(value=0.5, rationale=f"Could not parse evaluation: {result}")
            
    except Exception as e:
        return Feedback(value=0.0, rationale=f"Evaluation error: {str(e)}")


@scorer
def is_accurate(outputs: str, expectations: dict) -> Feedback:
    """
    Evaluate if the response is factually accurate.
    
    This scorer assesses the factual correctness of the response based on
    established knowledge and verifiable information.
    """
    try:
        client = _get_groq_client()
        evaluation_prompt = [
            {"role": "system", "content": "You are an expert evaluator. Rate responses on a scale of 0-1 where 1 is perfect."},
            {"role": "user", "content": f"""
Evaluate this response for factual accuracy:

Response: "{outputs}"

Guidelines: The response should be factually accurate and based on established knowledge.
Consider whether the information presented is correct, verifiable, and reliable.

Provide your evaluation in this exact JSON format:
{{"score": 0.85, "rationale": "Brief explanation of your score"}}
"""}
        ]
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=evaluation_prompt,
            temperature=0.1,
            max_tokens=200,
        )
        
        result = response.choices[0].message.content
        try:
            eval_result = json.loads(result)
            return Feedback(value=eval_result["score"], rationale=eval_result["rationale"])
        except (json.JSONDecodeError, KeyError):
            return Feedback(value=0.5, rationale=f"Could not parse evaluation: {result}")
            
    except Exception as e:
        return Feedback(value=0.0, rationale=f"Evaluation error: {str(e)}")


@scorer
def is_helpful(outputs: str, expectations: dict) -> Feedback:
    """
    Evaluate if the response is helpful and addresses the question.
    
    This scorer assesses whether the response is useful, informative,
    and directly addresses what the user is asking for.
    """
    try:
        client = _get_groq_client()
        evaluation_prompt = [
            {"role": "system", "content": "You are an expert evaluator. Rate responses on a scale of 0-1 where 1 is perfect."},
            {"role": "user", "content": f"""
Evaluate this response for helpfulness:

Response: "{outputs}"

Guidelines: The response should be helpful, informative, and directly address the user's question.
Consider relevance, completeness, and practical value.

Provide your evaluation in this exact JSON format:
{{"score": 0.85, "rationale": "Brief explanation of your score"}}
"""}
        ]
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=evaluation_prompt,
            temperature=0.1,
            max_tokens=200,
        )
        
        result = response.choices[0].message.content
        try:
            eval_result = json.loads(result)
            return Feedback(value=eval_result["score"], rationale=eval_result["rationale"])
        except (json.JSONDecodeError, KeyError):
            return Feedback(value=0.5, rationale=f"Could not parse evaluation: {result}")
            
    except Exception as e:
        return Feedback(value=0.0, rationale=f"Evaluation error: {str(e)}")
