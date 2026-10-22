from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Text-to-SQL"
    debug: bool = False
    ollama_url : str = "http://127.0.0.1:9931/v1/chat/completions"
    model_name: str = "local-model"
    db_url: str = "sqlite:///./school.db"
    schema_path: str = "database_description.yaml"
    max_retries: int = 1
    clarification_signal_threshold: int = 2


    class Config:
        env_file = ".env"

settings = Settings()