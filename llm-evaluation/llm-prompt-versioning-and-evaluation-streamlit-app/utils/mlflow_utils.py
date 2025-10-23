import mlflow
from typing import List, Dict, Any


def setup_mlflow(tracking_uri: str, experiment_name: str) -> None:
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)


def ensure_prompt_registered(prompt_name: str, template: List[Dict[str, str]], commit_message: str) -> bool:
    """Register a prompt template as a new version in MLflow prompt registry.
    Only creates a new version if the template differs from the latest version.
    
    Returns:
        bool: True if a new version was created, False if template was identical to existing.
    """
    try:
        # Try to load the latest prompt to compare
        existing_prompt = mlflow.genai.load_prompt(f"prompts:/{prompt_name}@latest")
        existing_template = existing_prompt.template
        
        # Compare the templates (normalize by removing any extra whitespace)
        def normalize_template(tmpl):
            """Normalize template for comparison."""
            if isinstance(tmpl, list):
                return [{"role": item.get("role", "").strip(), 
                        "content": item.get("content", "").strip()} for item in tmpl]
            return tmpl
        
        if normalize_template(existing_template) == normalize_template(template):
            # Templates are identical, no need to create a new version
            print(f"Prompt '{prompt_name}' already has the same template. Skipping version creation.")
            return False
    except Exception:
        # Prompt doesn't exist yet, will create new one
        pass
    
    # Template is different or prompt doesn't exist, register new version
    mlflow.genai.register_prompt(name=prompt_name, template=template, commit_message=commit_message)
    return True


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


def check_prompt_exists(prompt_name: str) -> bool:
    """Check if a prompt exists without creating one."""
    try:
        mlflow.genai.load_prompt(f"prompts:/{prompt_name}@latest")
        return True
    except Exception:
        return False


def get_prompt_versions(prompt_name: str) -> List[Dict[str, Any]]:
    """Get all versions of a prompt."""
    try:
        # This would require MLflow client API to list prompt versions
        # For now, we'll return empty list as MLflow doesn't have a direct API for this
        return []
    except Exception:
        return []
