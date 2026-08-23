variable "project_name" {
  description = "Short name used as a prefix for all Azure resource names."
  type        = string
  default     = "entdemo"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "environment must be one of: dev, staging, production."
  }
}

variable "location" {
  description = "Azure region for all resources."
  type        = string
  default     = "eastus"
}

# --- Container Apps -----------------------------------------------------

variable "container_image" {
  description = <<-EOT
    Fully qualified container image reference for the API, e.g.
    myregistry.azurecr.io/enterprise-demo-cloud-app:latest.
    Defaults to a placeholder image so `terraform plan` works before Phase 7
    wires up a real registry and CI-built image.
  EOT
  type        = string
  default     = "docker.io/library/hello-world:latest"
}

variable "container_cpu" {
  description = "vCPU allocation per replica. Must be a value supported by Container Apps (e.g. 0.25, 0.5, 1.0) and pair validly with container_memory."
  type        = number
  default     = 0.5
}

variable "container_memory" {
  description = "Memory allocation per replica (e.g. \"1Gi\"). Must pair validly with container_cpu."
  type        = string
  default     = "1Gi"
}

variable "min_replicas" {
  description = "Minimum number of container app replicas."
  type        = number
  default     = 1
}

variable "max_replicas" {
  description = "Maximum number of container app replicas."
  type        = number
  default     = 5
}

# --- Redis ----------------------------------------------------------------

variable "redis_sku_name" {
  description = "Azure Cache for Redis SKU: Basic, Standard, or Premium."
  type        = string
  default     = "Standard"
}

variable "redis_family" {
  description = "Redis SKU family: C for Basic/Standard, P for Premium."
  type        = string
  default     = "C"
}

variable "redis_capacity" {
  description = "Redis capacity tier (0-6 for family C, 1-5 for family P)."
  type        = number
  default     = 1
}

# --- API Management ---------------------------------------------------------

variable "enable_apim" {
  description = "Whether to provision the API Management gateway. Off by default to skip its hourly billing (Developer SKU) until an auth/rate-limit policy justifies it."
  type        = bool
  default     = false
}

variable "apim_publisher_name" {
  description = "Publisher name shown in the APIM developer portal."
  type        = string
  default     = "Enterprise Demo Cloud App"
}

variable "apim_publisher_email" {
  description = "Publisher email required by APIM (notifications, developer portal)."
  type        = string
}

variable "apim_sku_name" {
  description = <<-EOT
    APIM SKU and capacity, e.g. Developer_1, Premium_1. VNet integration
    (used by this module for the "enterprise best practices" networking
    story) requires the Developer or Premium tier -- Basic/Standard/
    Consumption don't support it.
  EOT
  type        = string
  default     = "Developer_1"
}

# --- Shared -----------------------------------------------------------------

variable "tags" {
  description = "Common resource tags applied to every resource."
  type        = map(string)
  default = {
    project    = "enterprise-demo-cloud-app"
    managed_by = "terraform"
  }
}
