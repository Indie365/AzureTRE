variable "tre_id" {}
variable "location" {}
variable "resource_group_name" {}
variable "shared_subnet_id" {}
variable "enable_local_debugging" {}
variable "virtual_network_id" {}
variable "api_principal_id" {}

variable "docker_registry_server" {
  type        = string
  description = "Docker registry server"
}

variable "airlock_processor_image_repository" {
  type        = string
  description = "Repository for Airlock processor image"
  default     = "microsoft/azuretre/airlock-processor"
}

variable "mgmt_resource_group_name" {
  type        = string
  description = "Shared management resource group"
}

variable "mgmt_acr_name" {
  type        = string
  description = "Management ACR name"
}

variable "arm_subscription_id" {
  description = "The subscription id to create the resource processor permission/role. If not supplied will use the TF context."
  type        = string
  default     = ""
}
