from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Settings loaded from environment variables or .env file"""
    model_config = SettingsConfigDict(
        env_file=["../.env", ".env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True
    )
    
    # API Keys
    openai_api_key: str
    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_base_url: str  # Must come from env - no default!
    
    # CORS Configuration
    cors_origins: str = "*"  # Comma-separated list of allowed origins
    
    # Model Configuration
    chat_model_name: str = "gpt-5-mini"  # Text chat model
    multimodal_model_name: str = "gpt-5-mini"  # Multimodal model
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str = "https://foundry-service-lego.openai.azure.com"
    azure_openai_api_version: str = "2024-02-01"
    
    # Azure AI Foundry Configuration
    azure_ai_foundry_endpoint: str = "https://foundry-service-lego.cognitiveservices.azure.com/models"


# Load settings with error handling
try:
    settings = Settings()
    
    # Set Langfuse environment variables (required for decorator)
    os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
    os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
    os.environ["LANGFUSE_HOST"] = settings.langfuse_base_url
    
    logger.info("Configuration loaded successfully")
    logger.info(f"Langfuse URL: {settings.langfuse_base_url}")
    logger.info(f"Chat Model: {settings.chat_model_name}")
    logger.info(f"Multimodal Model: {settings.multimodal_model_name}")
    logger.info(f"OpenAI API Key: {'*' * 20}{settings.openai_api_key[-4:]}")
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error("Make sure these environment variables are set:")
    logger.error("- OPENAI_API_KEY")
    logger.error("- LANGFUSE_SECRET_KEY")
    logger.error("- LANGFUSE_PUBLIC_KEY")
    logger.error("- LANGFUSE_BASE_URL")
    logger.error("In Azure, these are managed by Terraform (see terraform/main.tf)")
    raise

