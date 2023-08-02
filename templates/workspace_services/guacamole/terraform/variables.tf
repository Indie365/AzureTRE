variable "workspace_id" {}
variable "aad_authority_url" {}
variable "tre_id" {}
variable "mgmt_resource_group_name" {}
variable "mgmt_acr_name" {}
variable "image_name" {}
variable "image_tag" {}
variable "guac_disable_copy" {}
variable "guac_disable_paste" {}
variable "guac_enable_drive" {}
variable "guac_drive_name" {}
variable "guac_drive_path" {}
variable "guac_disable_download" {}
variable "guac_disable_upload" {}
variable "is_exposed_externally" {}
variable "tre_resource_id" {}
variable "arm_environment" {}

variable "tags" {
  type        = map(string)
  description = "Tags to be applied to all resources"
  default     = {}
}
