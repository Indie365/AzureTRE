data "azurerm_resource_group" "ws" {
  name = "rg-${var.tre_id}-ws-${local.short_workspace_id}"
}

data "azurerm_virtual_network" "ws" {
  name                = "vnet-${var.tre_id}-ws-${local.short_workspace_id}"
  resource_group_name = data.azurerm_resource_group.ws.name
}

data "azurerm_subnet" "services" {
  name                 = "ServicesSubnet"
  virtual_network_name = data.azurerm_virtual_network.ws.name
  resource_group_name  = data.azurerm_resource_group.ws.name
}

data "azurerm_key_vault" "ws" {
  name                = local.keyvault_name
  resource_group_name = data.azurerm_resource_group.ws.name
}

data "azurerm_linux_web_app" "guacamole" {
  name                = "guacamole-${var.tre_id}-ws-${local.short_workspace_id}-svc-${local.short_parent_id}"
  resource_group_name = data.azurerm_resource_group.ws.name
}

data "azurerm_storage_container" "airlock_request_container" {
  name                 = var.airlock_request_id
  storage_account_name = local.import_in_progress_storage_name
}
