output "resource_group_name" {
  description = "Name of the resource group holding all Phase 6 Azure resources."
  value       = azurerm_resource_group.main.name
}

output "container_app_fqdn" {
  description = "Public FQDN of the container app (bypasses APIM)."
  value       = module.azure.container_app_fqdn
}

output "apim_gateway_url" {
  description = "Public API Management gateway URL clients should call."
  value       = module.azure.apim_gateway_url
}

output "redis_hostname" {
  description = "Azure Cache for Redis hostname."
  value       = module.azure.redis_hostname
}

output "redis_ssl_port" {
  description = "Azure Cache for Redis TLS port."
  value       = module.azure.redis_ssl_port
}

output "app_insights_connection_string" {
  description = "Application Insights connection string for the API."
  value       = module.azure.app_insights_connection_string
  sensitive   = true
}

output "container_apps_subnet_id" {
  description = "Subnet ID used by the Container Apps environment (for peering/private endpoints later)."
  value       = module.azure.container_apps_subnet_id
}

output "acr_login_server" {
  description = "Login server of the Azure Container Registry. Use with `az acr build` to push images."
  value       = module.azure.acr_login_server
}

output "acr_name" {
  description = "Name of the Azure Container Registry (for `az acr build -r <name>`)."
  value       = module.azure.acr_name
}
