# External VNet mode: APIM is reachable from the internet as the gateway
# clients call, while its dependency traffic runs through snet-apim.
# VNet injection requires Developer or Premium SKU (see variables.tf).

resource "azurerm_api_management" "main" {
  count = var.enable_apim ? 1 : 0

  name                = "apim-${local.name_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  publisher_name      = var.apim_publisher_name
  publisher_email     = var.apim_publisher_email
  sku_name            = var.apim_sku_name
  tags                = var.tags

  virtual_network_type = "External"

  virtual_network_configuration {
    subnet_id = azurerm_subnet.apim.id
  }

  # APIM's control plane needs the NSG rules in place (specifically the
  # ApiManagement/3443 and AzureLoadBalancer/6390 inbound allows) before it
  # can finish provisioning into the subnet.
  depends_on = [azurerm_subnet_network_security_group_association.apim]
}

resource "azurerm_api_management_api" "main" {
  count = var.enable_apim ? 1 : 0

  name                = "enterprise-demo-api"
  resource_group_name = var.resource_group_name
  api_management_name = azurerm_api_management.main[0].name
  revision            = "1"
  display_name        = "Enterprise Demo Cloud App API"
  path                = "api"
  protocols           = ["https"]
  service_url         = "https://${azurerm_container_app.main.ingress[0].fqdn}"

  # No auth enforced yet -- Iteration 3 adds OAuth2/OIDC per PLAN.md. Until
  # then this mirrors the app's current unauthenticated endpoints.
  subscription_required = false
}

resource "azurerm_api_management_api_operation" "health_live" {
  count = var.enable_apim ? 1 : 0

  operation_id        = "get-health-live"
  api_name            = azurerm_api_management_api.main[0].name
  api_management_name = azurerm_api_management.main[0].name
  resource_group_name = var.resource_group_name
  display_name        = "Liveness check"
  method              = "GET"
  url_template        = "/v1/health/live"

  response {
    status_code = 200
  }
}

resource "azurerm_api_management_api_operation" "about" {
  count = var.enable_apim ? 1 : 0

  operation_id        = "get-about"
  api_name            = azurerm_api_management_api.main[0].name
  api_management_name = azurerm_api_management.main[0].name
  resource_group_name = var.resource_group_name
  display_name        = "About"
  method              = "GET"
  url_template        = "/v1/about"

  response {
    status_code = 200
  }
}
