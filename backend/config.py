from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """Settings loaded from environment variables or .env file"""
    model_config = SettingsConfigDict(
        env_file=["../.env", ".env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True
    )
    
    openai_api_key: str
    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_base_url: str = "http://langfuse.legocase.com"


# Load settings
settings = Settings()

# Set Langfuse environment variables (required for decorator)
os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
os.environ["LANGFUSE_HOST"] = settings.langfuse_base_url

