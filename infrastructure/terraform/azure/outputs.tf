output "container_app_fqdn" {
  description = "Public FQDN of the container app (bypasses APIM)."
  value       = azurerm_container_app.main.ingress[0].fqdn
}

output "apim_gateway_url" {
  description = "Public API Management gateway URL clients should call. Null when enable_apim is false."
  value       = var.enable_apim ? azurerm_api_management.main[0].gateway_url : null
}

output "redis_hostname" {
  description = "Azure Cache for Redis hostname."
  value       = azurerm_redis_cache.main.hostname
}

output "redis_ssl_port" {
  description = "Azure Cache for Redis TLS port."
  value       = azurerm_redis_cache.main.ssl_port
}

output "app_insights_connection_string" {
  description = "Application Insights connection string for the API."
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "container_apps_subnet_id" {
  description = "Subnet ID used by the Container Apps environment."
  value       = azurerm_subnet.container_apps.id
}

output "acr_login_server" {
  description = "Login server of the Azure Container Registry, e.g. acrentdemodev.azurecr.io. Use with `az acr build` to push images."
  value       = azurerm_container_registry.main.login_server
}

output "acr_name" {
  description = "Name of the Azure Container Registry (for `az acr build -r <name>`)."
  value       = azurerm_container_registry.main.name
}
