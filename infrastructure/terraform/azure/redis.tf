resource "azurerm_redis_cache" "main" {
  name                = "redis-${local.name_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name

  capacity             = var.redis_capacity
  family               = var.redis_family
  sku_name             = var.redis_sku_name
  non_ssl_port_enabled = false
  minimum_tls_version  = "1.2"

  tags = var.tags
}
