resource "azurerm_network_interface" "internal" {
  name                = "internal-nic-${local.service_resource_name_suffix}"
  location            = data.azurerm_resource_group.ws.location
  resource_group_name = data.azurerm_resource_group.ws.name
  tags                = local.tre_user_resources_tags

  ip_configuration {
    name                          = "primary"
    subnet_id                     = data.azurerm_subnet.services.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "random_string" "username" {
  length      = 4
  upper       = true
  lower       = true
  numeric     = true
  min_numeric = 1
  min_lower   = 1
  special     = false
}

resource "random_password" "password" {
  length           = 16
  lower            = true
  min_lower        = 1
  upper            = true
  min_upper        = 1
  numeric          = true
  min_numeric      = 1
  special          = true
  min_special      = 1
  override_special = "_%@"
}

resource "azurerm_windows_virtual_machine" "windowsvm" {
  name                       = local.vm_name
  location                   = data.azurerm_resource_group.ws.location
  resource_group_name        = data.azurerm_resource_group.ws.name
  network_interface_ids      = [azurerm_network_interface.internal.id]
  size                       = local.vm_size
  allow_extension_operations = true
  admin_username             = random_string.username.result
  admin_password             = random_password.password.result

  custom_data = base64encode(data.template_file.vm_config.rendered)

  source_image_reference {
    publisher = local.image_ref.publisher
    offer     = local.image_ref.offer
    sku       = local.image_ref.sku
    version   = local.image_ref.version
  }

  os_disk {
    name                 = "osdisk-${local.vm_name}"
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = local.tre_user_resources_tags
}

resource "azurerm_virtual_machine_extension" "config_script" {
  name                 = "${azurerm_windows_virtual_machine.windowsvm.name}-vmextension"
  virtual_machine_id   = azurerm_windows_virtual_machine.windowsvm.id
  publisher            = "Microsoft.Compute"
  type                 = "CustomScriptExtension"
  type_handler_version = "1.10"
  tags                 = local.tre_user_resources_tags

  protected_settings = <<PROT
    {
      "commandToExecute": "powershell -ExecutionPolicy Unrestricted -NoProfile -NonInteractive -command \"cp c:/azuredata/customdata.bin c:/azuredata/configure.ps1; c:/azuredata/configure.ps1 \""
    }
PROT
}

resource "azurerm_key_vault_secret" "windowsvm_password" {
  name         = "${local.vm_name}-admin-credentials"
  value        = "${random_string.username.result}\n${random_password.password.result}"
  key_vault_id = data.azurerm_key_vault.ws.id
  tags         = local.tre_user_resources_tags
}

data "template_file" "vm_config" {
  template = file("${path.module}/download_container.ps1")
  vars = {
    import_in_progress_storage = local.import_in_progress_storage_name
    container_name             = var.airlock_request_id
  }
}

resource "azurerm_role_assignment" "container_blob_data_reader_reviewer_vm" {
  scope                = data.azurerm_storage_container.airlock_request_container.resource_manager_id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_windows_virtual_machine.windowsvm.identity.0.principal_id

  depends_on = [
    azurerm_windows_virtual_machine.windowsvm
  ]
}
