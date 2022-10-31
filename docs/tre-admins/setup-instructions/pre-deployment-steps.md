# Pre-deployment steps

!!! info
    See [Environment variables](../environment-variables.md) for full details of the deployment related variables.

## Set environment configuration variables of shared management resources

1. Open the `/devops/.env.sample` file and then save it without the .sample extension. You should now have a file called `.env` located in the `/devops` folder. The file contains configuration variables for the shared management infrastructure which is used to support the deployment of one or more Azure TRE instances.

2. Provide the values for the following variables:

  | Variable | Description |
  | -------- | ----------- |
  | `LOCATION` | The [Azure location (region)](https://azure.microsoft.com/global-infrastructure/geographies/#geographies) for all resources. E.g., `westeurope` |
  | `MGMT_RESOURCE_GROUP_NAME` | The shared resource group for all management resources, including the storage account. |
  | `MGMT_STORAGE_ACCOUNT_NAME` | The name of the storage account to hold the Terraform state and other deployment artifacts. |
  | `ACR_NAME` | A globally unique name for the [Azure Container Registry (ACR)](https://docs.microsoft.com/azure/container-registry/) that will be created to store deployment images. |
  | `ARM_SUBSCRIPTION_ID` | The Azure subscription ID for all resources. |

  !!! tip
      To retrieve your Azure subscription ID, use the `az` command line interface available in the development container. In the terminal window in Visual Studio Code, type `az login` followed by `az account show` to see your default subscription. Please refer to `az account -help` for further details on how to change your active subscription.

The rest of the variables can have their default values. You should now have a `.env` file that looks similar to the one below:

```plaintext
# Management infrastructure
LOCATION=westeurope
MGMT_RESOURCE_GROUP_NAME=aztremgmt
MGMT_STORAGE_ACCOUNT_NAME=aztremgmt
TERRAFORM_STATE_CONTAINER_NAME=tfstate
ACR_NAME=aztreacr

ARM_SUBSCRIPTION_ID=12...54e

# If you want to override the currently signed in credentials
# ARM_TENANT_ID=__CHANGE_ME__
# ARM_CLIENT_ID=__CHANGE_ME__
# ARM_CLIENT_SECRET=__CHANGE_ME__

# Debug mode
DEBUG="false"
```

## Set environment configuration variables of the Azure TRE instance

Next, you will set the configuration variables for the specific Azure TRE instance:

1. Open the `/templates/core/.env.sample` file and then save it without the .sample extension. You should now have a file called `.env` located in the `/templates/core` folder.
1. Decide on a name for your `TRE_ID`, which is an alphanumeric (with underscores and hyphens allowed) ID for the Azure TRE instance. The value will be used in various Azure resources, and **needs to be globally unique and less than 12 characters in length**. Use only lowercase letters. Choose wisely!
1. Once you have decided on which AD Tenant paradigm, then you should be able to set `AAD_TENANT_ID`
1. If you want to disable the built-in web UI (`./ui`) ensure you set `DEPLOY_UI=false` in the .env file.
1. Your AAD Tenant Admin can now use the terminal window in Visual Studio Code to execute the following script from within the development container to create all the AAD Applications that are used for TRE. The details of the script are covered in the [auth document](../auth.md).

   ```bash
   make auth
   ```

  !!! note
      In case you have several subscriptions and would like to change your default subscription use `az account set --subscription <desired subscription ID>`

  !!! note
      The full functionality of the script requires directory admin privileges. You may need to contact your friendly Azure Active Directory admin to complete this step. The app registrations can be created manually in Azure Portal too. For more information, see [Authentication and authorization](../auth.md).
  

All other variables can have their default values for now.

## Add admin user

Make sure the **TRE Administrators** and **TRE Users** roles, defined by the API app registration, are assigned to your user and others as required. See [Enabling users](../auth.md#enabling-users) for instructions.

## Next steps

* [Deploying Azure TRE](deploying-azure-tre.md)