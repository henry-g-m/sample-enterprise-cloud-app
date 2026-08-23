variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "container_image" {
  type = string
}

variable "container_cpu" {
  type = number
}

variable "container_memory" {
  type = string
}

variable "min_replicas" {
  type = number
}

variable "max_replicas" {
  type = number
}

variable "redis_sku_name" {
  type = string
}

variable "redis_family" {
  type = string
}

variable "redis_capacity" {
  type = number
}

variable "apim_publisher_name" {
  type = string
}

variable "apim_publisher_email" {
  type = string
}

variable "enable_apim" {
  description = "Whether to provision the API Management gateway. Off by default to skip its hourly billing (Developer SKU) until an auth/rate-limit policy justifies it -- see api-management.tf."
  type        = bool
  default     = false
}

variable "apim_sku_name" {
  type = string
}

variable "tags" {
  type = map(string)
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}
