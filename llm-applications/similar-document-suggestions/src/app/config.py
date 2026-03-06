from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/confluence_reco"
    gemini_api_key: str | None = None
    gemini_embedding_model: str = "models/embedding-001"
    embedding_dim: int = 768
    data_dir: str = "./data"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
