import os
import mlflow
from typing import List, Dict, Any


def setup_mlflow(tracking_uri: str, experiment_name: str) -> None:
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)


def ensure_prompt_registered(prompt_name: str, template: List[Dict[str, str]], commit_message: str) -> None:
    """Register a prompt template as a new version in MLflow prompt registry."""
    mlflow.genai.register_prompt(name=prompt_name, template=template, commit_message=commit_message)


def load_latest_prompt(prompt_name: str):
    return mlflow.genai.load_prompt(f"prompts:/{prompt_name}@latest")


def ensure_default_prompt_exists(prompt_name: str) -> bool:
    """Ensure a default prompt exists, create one if it doesn't."""
    try:
        # Try to load the latest prompt
        mlflow.genai.load_prompt(f"prompts:/{prompt_name}@latest")
        return True
    except Exception:
        # Prompt doesn't exist, create a default one
        try:
            default_template = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer the following question in three sentences or less. Be concise and professional.",
                },
                {
                    "role": "user",
                    "content": "Question: {{question}}",
                },
            ]
            mlflow.genai.register_prompt(
                name=prompt_name,
                template=default_template,
                commit_message="Default prompt created automatically"
            )
            return True
        except Exception as e:
            print(f"Failed to create default prompt: {e}")
            return False
