locals {
  # var.environment ("dev"/"staging"/"production") drives resource naming
  # (rg-entdemo-dev, etc.) and can't change without recreating every named
  # resource. src/config/settings.py's Settings.environment (and CLAUDE.md)
  # expect the spelled-out "development" instead, so translate only the
  # value sent into the container -- not the naming variable itself.
  app_environment = var.environment == "dev" ? "development" : var.environment
}

resource "azurerm_container_app_environment" "main" {
  name                       = "cae-${local.name_prefix}"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  infrastructure_subnet_id   = azurerm_subnet.container_apps.id
  tags                       = var.tags

  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }
}

resource "azurerm_container_app" "main" {
  name                         = "ca-${local.name_prefix}"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  tags                         = var.tags

  # AcrPull must already be granted before this resource is created, or the
  # first revision fails to pull the image. See container-registry.tf.
  depends_on = [azurerm_role_assignment.acr_pull]

  identity {
    type         = "SystemAssigned, UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.container_app.id]
  }

  registry {
    server   = azurerm_container_registry.main.login_server
    identity = azurerm_user_assigned_identity.container_app.id
  }

  secret {
    name  = "redis-password"
    value = azurerm_redis_cache.main.primary_access_key
  }

  secret {
    name  = "app-insights-connection-string"
    value = azurerm_application_insights.main.connection_string
  }

  template {
    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    container {
      name   = "api"
      image  = var.container_image
      cpu    = var.container_cpu
      memory = var.container_memory

      # Mirrors src/config/settings.py's Settings fields.
      env {
        name  = "ENVIRONMENT"
        value = local.app_environment
      }

      env {
        name  = "REDIS_HOST"
        value = azurerm_redis_cache.main.hostname
      }

      env {
        name  = "REDIS_PORT"
        value = tostring(azurerm_redis_cache.main.ssl_port)
      }

      env {
        name  = "REDIS_SSL"
        value = "true"
      }

      env {
        name        = "REDIS_PASSWORD"
        secret_name = "redis-password"
      }

      env {
        name  = "ENABLE_APP_INSIGHTS"
        value = "true"
      }

      env {
        name        = "APP_INSIGHTS_CONNECTION_STRING"
        secret_name = "app-insights-connection-string"
      }

      liveness_probe {
        transport = "HTTP"
        path      = "/api/v1/health/live"
        port      = 8000
      }

      readiness_probe {
        transport = "HTTP"
        path      = "/api/v1/health/ready"
        port      = 8000
      }

      startup_probe {
        transport = "HTTP"
        path      = "/api/v1/health/startup"
        port      = 8000
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
}
