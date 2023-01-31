resource "azurerm_databricks_workspace" "databricks" {
  name                                  = local.databricks_workspace_name
  resource_group_name                   = data.azurerm_resource_group.ws.name
  location                              = data.azurerm_resource_group.ws.location
  sku                                   = "premium"
  managed_resource_group_name           = local.managed_resource_group_name
  infrastructure_encryption_enabled     = true
  public_network_access_enabled         = var.is_exposed_externally
  network_security_group_rules_required = var.is_exposed_externally ? "AllRules" : "NoAzureDatabricksRules"
  tags                                  = local.tre_workspace_service_tags

  lifecycle { ignore_changes = [tags] }

  custom_parameters {
    no_public_ip                                         = true
    public_subnet_name                                   = azurerm_subnet.host.name
    private_subnet_name                                  = azurerm_subnet.container.name
    virtual_network_id                                   = data.azurerm_virtual_network.ws.id
    public_subnet_network_security_group_association_id  = azurerm_subnet_network_security_group_association.host.id
    private_subnet_network_security_group_association_id = azurerm_subnet_network_security_group_association.container.id
    storage_account_name                                 = local.storage_name
  }

  depends_on = [
    azurerm_subnet_network_security_group_association.host,
    azurerm_subnet_network_security_group_association.container
  ]
}
