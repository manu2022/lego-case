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
    langfuse_base_url: str  # Must come from env - no default!
    cors_origins: str = "*"  # Comma-separated list of allowed origins


# Load settings with error handling
try:
    settings = Settings()
    
    # Set Langfuse environment variables (required for decorator)
    os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
    os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
    os.environ["LANGFUSE_HOST"] = settings.langfuse_base_url
    
    print("✅ Configuration loaded successfully")
    print(f"   Langfuse URL: {settings.langfuse_base_url}")
    print(f"   OpenAI API Key: {'*' * 20}{settings.openai_api_key[-4:]}")
except Exception as e:
    print(f"❌ Error loading configuration: {e}")
    print(f"   Make sure these environment variables are set:")
    print(f"   - OPENAI_API_KEY")
    print(f"   - LANGFUSE_SECRET_KEY")
    print(f"   - LANGFUSE_PUBLIC_KEY")
    print(f"   - LANGFUSE_BASE_URL")
    print(f"\n   In Azure, these are managed by Terraform (see terraform/main.tf)")
    raise

