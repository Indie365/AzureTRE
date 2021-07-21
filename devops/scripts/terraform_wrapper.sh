#!/bin/bash
set -e


function usage() {
    cat <<USAGE

    Usage: $0 [-g | --mgmt-resource-group-name ]  [-s | --mgmt-storage-account-name] [-n | --state-container-name] [-k | --key] [-c | --cmd]

    Options:
        -g, --mgmt-resource-group-name      Management resource group name
        -s, --mgmt-storage-account-name     Management storage account name
        -n, --state-container-name          State container name
        -k, --key                           Key
        -c, --cmd                           Command to execute
USAGE
    exit 1
}

# if no arguments are provided, return usage function
if [ $# -eq 0 ]; then
    usage # run usage function
fi

current="false"

while [ "$1" != "" ]; do
    case $1 in
    -g | --mgmt-resource-group-name)
        shift
        mgmt_resource_group_name=$1
        ;;
    -s | --mgmt-storage-account-name)
        shift
        mgmt_storage_account_name=$1
        ;;
    -n | --state-container-name)
        shift
        container_name=$1
        ;;
    -k | --key)
        shift
        key=$1
        ;;
    -c | --cmd)
        shift
        tf_command=$1
        ;;
    *)
        usage
        ;;
    esac
    shift # remove the current value for `$1` and use the next
done


if [[ -z ${mgmt_resource_group_name+x} ]]; then  
    echo -e "No terraform state resource group name provided\n"
    usage
fi

if [[ -z ${mgmt_storage_account_name+x} ]]; then  
    echo -e "No terraform state storage account name provided\n"
    usage
fi

if [[ -z ${container_name+x} ]]; then  
    echo -e "No terraform state container name provided\n"
    usage
fi

if [[ -z ${key+x} ]]; then 
    echo -e "No key provided\n"
    usage
fi

if [[ -z ${tf_command+x} ]]; then 
    echo -e "No command provided\n"
    usage
fi

export TF_LOG=""
terraform init -input=false -backend=true -reconfigure -upgrade \
    -backend-config="resource_group_name=${mgmt_resource_group_name}" \
    -backend-config="storage_account_name=${mgmt_storage_account_name}" \
    -backend-config="container_name=${container_name}" \
    -backend-config="key=${key}"

RUN_COMMAND=1
LOG_FILE="tmp$$.log"
while [ $RUN_COMMAND = 1 ]
do 
    RUN_COMMAND=0
    TF_CMD="$tf_command"
  
    script -c "$TF_CMD" $LOG_FILE

    LOCKED_STATE=$(cat tmp$$.log |  grep -c 'Error acquiring the state lock') || true; 
    TF_ERROR=$(cat tmp$$.log |  grep -c 'Error') || true; 
    if [[ $LOCKED_STATE > 0  ]];
    then
        RUN_COMMAND=1
        echo "Error acquiring the state lock"
        sleep 10
    elif [[ $TF_ERROR > 0  ]];
    then
        echo "Terraform Error"
        exit 1
    fi
done