# Use existing resource group
data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

# Locals for common values
locals {
  location = data.azurerm_resource_group.rg.location
  rg_name  = data.azurerm_resource_group.rg.name
}

# Random suffix for globally unique container registry name
resource "random_string" "acr_name" {
  length  = 5
  lower   = true
  numeric = false
  special = false
  upper   = false
}

# Container Registry
resource "azurerm_container_registry" "acr" {
  name                = "${random_string.acr_name.result}registry"
  resource_group_name = local.rg_name
  location            = local.location
  sku                 = "Standard"
  admin_enabled       = true  # Needed for CI/CD to push images
}

# App Service Plan
resource "azurerm_service_plan" "app" {
  name                = "question-answer-plan"
  location            = local.location
  resource_group_name = local.rg_name
  os_type             = "Linux"
  sku_name            = "B1"
}

# Web App with Managed Identity
resource "azurerm_linux_web_app" "app" {
  name                = "question-answer-api"
  location            = local.location
  resource_group_name = local.rg_name
  service_plan_id     = azurerm_service_plan.app.id

  identity {
    type = "SystemAssigned"
  }

  site_config {
    container_registry_use_managed_identity = true
    always_on                               = false  # Not available in Basic tier
    
    application_stack {
      docker_image_name   = "question-answer-api:latest"
      docker_registry_url = "https://${azurerm_container_registry.acr.login_server}"
    }
  }

  app_settings = {
    # Docker settings (no credentials needed - using managed identity!)
    WEBSITES_PORT                       = "8000"
    DOCKER_REGISTRY_SERVER_URL          = "https://${azurerm_container_registry.acr.login_server}"
    DOCKER_ENABLE_CI                    = "false"  # Disable CI/CD webhook - we use GitHub Actions
    WEBSITES_CONTAINER_START_TIME_LIMIT = "600"
    
    # Application environment variables
    OPENAI_API_KEY      = var.openai_api_key
    LANGFUSE_SECRET_KEY = var.langfuse_secret_key
    LANGFUSE_PUBLIC_KEY = var.langfuse_public_key
    LANGFUSE_BASE_URL   = var.langfuse_base_url
    CORS_ORIGINS        = "*"  # Will be updated by CI/CD to specific frontend URL
  }
  
  # Prevent unnecessary redeployments
  lifecycle {
    ignore_changes = [
      site_config[0].application_stack[0].docker_image_name
    ]
  }
}

# Grant Web App permission to pull images from Container Registry
resource "azurerm_role_assignment" "acr_pull" {
  principal_id                     = azurerm_linux_web_app.app.identity.0.principal_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.acr.id
  skip_service_principal_aad_check = true
  depends_on                       = [azurerm_linux_web_app.app]
}

# Webhook removed - using GitHub Actions for deployments instead
# The webhook can cause issues with the new sidecar configuration pattern
# and is redundant since GitHub Actions handles container updates

# Frontend Web App
resource "azurerm_linux_web_app" "frontend" {
  name                = "question-answer-frontend"
  location            = local.location
  resource_group_name = local.rg_name
  service_plan_id     = azurerm_service_plan.app.id

  identity {
    type = "SystemAssigned"
  }

  site_config {
    container_registry_use_managed_identity = true
    always_on                               = false  # Not available in Basic tier
    
    application_stack {
      docker_image_name   = "question-answer-frontend:latest"
      docker_registry_url = "https://${azurerm_container_registry.acr.login_server}"
    }
  }

  app_settings = {
    # Docker settings (no credentials needed - using managed identity!)
    WEBSITES_PORT                       = "80"
    DOCKER_REGISTRY_SERVER_URL          = "https://${azurerm_container_registry.acr.login_server}"
    DOCKER_ENABLE_CI                    = "false"  # Disable CI/CD webhook - we use GitHub Actions
    WEBSITES_CONTAINER_START_TIME_LIMIT = "600"
    
    # Application environment variables
    # VITE_API_URL will be set by CI/CD after backend is deployed
  }
  
  # Prevent unnecessary redeployments
  lifecycle {
    ignore_changes = [
      site_config[0].application_stack[0].docker_image_name
    ]
  }
}

# Grant Frontend Web App permission to pull images from Container Registry
resource "azurerm_role_assignment" "acr_pull_frontend" {
  principal_id                     = azurerm_linux_web_app.frontend.identity.0.principal_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.acr.id
  skip_service_principal_aad_check = true
  depends_on                       = [azurerm_linux_web_app.frontend]
}