from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tmdb_api_key: str
    openai_api_key: str
    firebase_service_account_path: str
    chroma_persist_dir: str = "./data/chroma_db"
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    frontend_url: str = "http://localhost:3000"
    candidate_count: int = 50
    result_count: int = 10
    embedding_model: str = "text-embedding-3-small"
    rerank_model: str = "gpt-4o-mini"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
