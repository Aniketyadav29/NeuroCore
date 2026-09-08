from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "NeuroCore AI"
    app_env: str = "development"
    frontend_url: str = "http://localhost:5173"

    database_url: str = "sqlite:///./neurocore.db"
    chroma_persist_dir: str = "./chroma_store"

    llm_provider: str = "offline"  # gemini | openai | groq | offline
    gemini_api_key: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
