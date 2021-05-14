from azure.core import exceptions
from azure.cosmos import CosmosClient
from api.core.config import STATE_STORE_ENDPOINT, STATE_STORE_KEY
from api.models.schemas.health import StatusEnum
from api.resources import strings


def get_state_store_status() -> (StatusEnum, str):
    status = StatusEnum.ok
    message = ""
    try:
        client = CosmosClient(STATE_STORE_ENDPOINT, STATE_STORE_KEY)    # noqa: F841 - flake 8 client is not used
    except exceptions.ServiceRequestError:
        status = StatusEnum.not_ok
        message = strings.STATE_STORE_ENDPOINT_NOT_RESPONDING
    except:     # noqa: E722 flake8 - no bare excepts
        status = StatusEnum.not_ok
        message = strings.UNSPECIFIED_ERROR
    return status, message
