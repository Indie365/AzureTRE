data "azurerm_resource_group" "rg" {
  name = local.resource_group_name
}

data "azurerm_virtual_network" "ws" {
  name                = local.virtual_network_name
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_firewall" "firewall" {
  name                = local.firewall_name
  resource_group_name = local.core_resource_group_name
}