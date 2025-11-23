output "resource_group_name" {
  value = data.azurerm_resource_group.rg.name
}

output "container_registry_name" {
  value = azurerm_container_registry.example.name
}

output "container_registry_login_server" {
  value = azurerm_container_registry.example.login_server
}

output "web_app_url" {
  value = "https://${azurerm_linux_web_app.app.default_hostname}"
}

output "web_app_name" {
  value = azurerm_linux_web_app.app.name
}

output "webhook_status" {
  value = "Continuous deployment enabled - webhook: ${azurerm_container_registry_webhook.app_webhook.name}"
}