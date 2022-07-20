variable "tre_id" {
  type        = string
  description = "Unique TRE ID"
}

variable "tre_resource_id" {
  type        = string
  description = "Resource ID"
}

variable "arm_subscription_id" {
  description = "The TRE subscription id."
  type        = string
  default     = ""
}

variable "smtp_server_address" {
  type = string
}

variable "smtp_username" {
  type = string
}

variable "smtp_password" {
  type      = string
  sensitive = true
}

variable "smtp_from_email" {
  type = string
}
