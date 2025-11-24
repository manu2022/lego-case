output "resource_group_name" {
  value       = data.azurerm_resource_group.rg.name
  description = "Resource group name"
}

output "container_registry_name" {
  value       = azurerm_container_registry.acr.name
  description = "Container registry name"
}

output "container_registry_login_server" {
  value       = azurerm_container_registry.acr.login_server
  description = "Container registry login server URL"
}

output "web_app_url" {
  value       = "https://${azurerm_linux_web_app.app.default_hostname}"
  description = "Web app public URL"
}

output "web_app_name" {
  value       = azurerm_linux_web_app.app.name
  description = "Web app name"
}

output "frontend_app_url" {
  value       = "https://${azurerm_linux_web_app.frontend.default_hostname}"
  description = "Frontend web app public URL"
}

output "frontend_app_name" {
  value       = azurerm_linux_web_app.frontend.name
  description = "Frontend web app name"
}