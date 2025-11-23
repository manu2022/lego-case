data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

resource "random_string" "acr_name" {
  length  = 5
  lower   = true
  numeric = false
  special = false
  upper   = false
}

resource "azurerm_container_registry" "example" {
  name                = "${random_string.acr_name.result}registry"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  sku                 = "Standard"
  admin_enabled       = true
}

resource "azurerm_service_plan" "app" {
  name                = "question-answer-plan"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "app" {
  name                = "question-answer-api"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.app.id

  site_config {
    application_stack {
      docker_image_name   = "question-answer-api:latest"
      docker_registry_url = "https://${azurerm_container_registry.example.login_server}"
    }
  }

  app_settings = {
    "WEBSITES_PORT"                       = "8000"
    "DOCKER_REGISTRY_SERVER_URL"          = "https://${azurerm_container_registry.example.login_server}"
    "DOCKER_REGISTRY_SERVER_USERNAME"     = azurerm_container_registry.example.admin_username
    "DOCKER_REGISTRY_SERVER_PASSWORD"     = azurerm_container_registry.example.admin_password
    "DOCKER_ENABLE_CI"                    = "true"
    "OPENAI_API_KEY"                      = var.openai_api_key
    "LANGFUSE_SECRET_KEY"                 = var.langfuse_secret_key
    "LANGFUSE_PUBLIC_KEY"                 = var.langfuse_public_key
    "LANGFUSE_BASE_URL"                   = var.langfuse_base_url
  }
}

data "azurerm_linux_web_app" "app_data" {
  name                = azurerm_linux_web_app.app.name
  resource_group_name = data.azurerm_resource_group.rg.name
  depends_on          = [azurerm_linux_web_app.app]
}

resource "azurerm_container_registry_webhook" "app_webhook" {
  name                = "questionanswerwebhook"
  resource_group_name = data.azurerm_resource_group.rg.name
  registry_name       = azurerm_container_registry.example.name
  location            = data.azurerm_resource_group.rg.location

  service_uri = "https://${data.azurerm_linux_web_app.app_data.site_credential[0].name}:${data.azurerm_linux_web_app.app_data.site_credential[0].password}@${azurerm_linux_web_app.app.name}.scm.azurewebsites.net/api/registry/webhook"
  actions     = ["push"]
  status      = "enabled"
  scope       = "question-answer-api:*"
}