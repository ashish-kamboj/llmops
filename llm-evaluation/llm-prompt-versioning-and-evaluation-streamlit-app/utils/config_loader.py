import os
import yaml
from typing import Any, Dict
from dotenv import load_dotenv


def load_configs(config_path: str) -> Dict[str, Any]:
    # Load .env file from the same directory as configs.yaml
    config_dir = os.path.dirname(config_path)
    env_path = os.path.join(config_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Allow environment variable overrides for MLflow and model params
    cfg["mlflow"]["tracking_uri"] = os.getenv("MLFLOW_TRACKING_URI", cfg["mlflow"]["tracking_uri"])
    cfg["mlflow"]["experiment_name"] = os.getenv("MLFLOW_EXPERIMENT", cfg["mlflow"]["experiment_name"])
    cfg["mlflow"]["prompt_name"] = os.getenv("PROMPT_NAME", cfg["mlflow"]["prompt_name"])

    cfg["llm"]["model"] = os.getenv("LLM_MODEL", cfg["llm"]["model"])
    cfg["llm"]["temperature"] = float(os.getenv("LLM_TEMPERATURE", cfg["llm"]["temperature"]))
    cfg["llm"]["max_tokens"] = int(os.getenv("LLM_MAX_TOKENS", cfg["llm"]["max_tokens"]))

    return cfg
