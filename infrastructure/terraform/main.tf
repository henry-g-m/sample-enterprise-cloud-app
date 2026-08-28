# Root Terraform configuration for the Azure deployment (Phase 6).
#
# This root module owns the resource group and provider configuration, then
# delegates actual resource definitions to ./azure so an equivalent ./aws
# module (Iteration 1's alternative stack) can be added later without
# reshaping this file.

terraform {
  required_version = ">= 1.9.0"

  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      # Verify the latest 4.x (or current major) release on the Terraform
      # Registry before `terraform init` and bump this constraint.
      version = "~> 4.0"
    }
  }

  # Remote state in Azure Blob Storage (Phase 7). Values are non-secret
  # (resource group, storage account, container, blob key) and are supplied
  # via `-backend-config` at init time -- both from CI (repo variables) and
  # locally (infrastructure/terraform/backend.hcl, gitignored, see
  # backend.hcl.example) -- so nothing environment-specific is hardcoded here.
  # Auth uses the caller's Azure AD identity (az login locally, OIDC in CI)
  # rather than a storage account key.
  backend "azurerm" {
    use_azuread_auth = true
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location
  tags     = var.tags
}

module "azure" {
  source = "./azure"

  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  container_image  = var.container_image
  container_cpu    = var.container_cpu
  container_memory = var.container_memory
  min_replicas     = var.min_replicas
  max_replicas     = var.max_replicas

  redis_sku_name = var.redis_sku_name
  redis_family   = var.redis_family
  redis_capacity = var.redis_capacity

  enable_apim          = var.enable_apim
  apim_publisher_name  = var.apim_publisher_name
  apim_publisher_email = var.apim_publisher_email
  apim_sku_name        = var.apim_sku_name

  tags = var.tags
}
