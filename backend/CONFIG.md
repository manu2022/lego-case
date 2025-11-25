# Backend Configuration Guide

## Environment Variables

All configuration is managed through environment variables using Pydantic Settings.

### Required Variables

These must be set in your environment or `.env` file:

```bash
OPENAI_API_KEY=your_azure_openai_api_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_BASE_URL=https://your-langfuse-url.azurecontainerapps.io
```

### Optional Variables (with defaults)

#### CORS Configuration
```bash
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
# Default: "*" (all origins allowed)
```

#### Model Configuration
```bash
CHAT_MODEL_NAME=gpt-5-mini
# Default: "gpt-5-mini"
# The Azure OpenAI deployment name for text chat

MULTIMODAL_MODEL_NAME=Phi-4-multimodal-instruct
# Default: "Phi-4-multimodal-instruct"
# The Azure AI Foundry model name for multimodal (image/PDF) questions
```

#### Azure OpenAI Configuration
```bash
AZURE_OPENAI_ENDPOINT=https://foundry-service-lego.openai.azure.com
# Default: "https://foundry-service-lego.openai.azure.com"

AZURE_OPENAI_API_VERSION=2024-02-01
# Default: "2024-02-01"
```

#### Azure AI Foundry Configuration
```bash
AZURE_AI_FOUNDRY_ENDPOINT=https://foundry-service-lego.cognitiveservices.azure.com/models
# Default: "https://foundry-service-lego.cognitiveservices.azure.com/models"
```

## Using Different Models

To use a different model, simply set the environment variable:

### Example: Use GPT-4o for Chat
```bash
export CHAT_MODEL_NAME=gpt-4o
```

### Example: Use Different Multimodal Model
```bash
export MULTIMODAL_MODEL_NAME=gpt-4-vision
```

## Configuration in Azure

When deploying to Azure Container Apps, these environment variables are set via Terraform in `terraform/main.tf`:

```hcl
env {
  name  = "CHAT_MODEL_NAME"
  value = "gpt-5-mini"
}

env {
  name  = "MULTIMODAL_MODEL_NAME"
  value = "Phi-4-multimodal-instruct"
}
```

## Configuration File Structure

Configuration is loaded in this order:
1. Environment variables
2. `.env` file in backend directory
3. `../.env` file in project root
4. Default values defined in `config.py`

See `config.py` for the complete Settings class definition.

