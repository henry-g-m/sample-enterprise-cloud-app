# Azure Container Registry for the API image (Phase 7). Admin user stays
# disabled -- the container app authenticates via a user-assigned managed
# identity instead of a shared admin password.
#
# The identity and its AcrPull role assignment are created here, ahead of
# the container app, specifically so there's no dependency cycle: granting
# AcrPull to a system-assigned identity would require the role assignment to
# depend on the container app's identity while the container app's registry
# block depends on the role already existing. A user-assigned identity lets
# both sides be provisioned in the correct order in one `apply`.

resource "azurerm_container_registry" "main" {
  name                = "acr${replace(local.name_prefix, "-", "")}"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = false
  tags                = var.tags
}

resource "azurerm_user_assigned_identity" "container_app" {
  name                = "id-${local.name_prefix}-aca"
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags
}

resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.container_app.principal_id
}
