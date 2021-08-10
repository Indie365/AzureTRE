import pytest
from mock import patch

from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from api.routes.workspaces import get_current_user
from db.errors import EntityDoesNotExist
from models.domain.authentication import User
from models.domain.resource import Status, Deployment
from models.domain.workspace import Workspace
from models.domain.workspace_service import WorkspaceService
from resources import strings


pytestmark = pytest.mark.asyncio


def create_sample_workspace_object(workspace_id, auth_info: dict = None):
    workspace = Workspace(
        id=workspace_id,
        description="My workspace",
        resourceTemplateName="tre-workspace-vanilla",
        resourceTemplateVersion="0.1.0",
        resourceTemplateParameters={},
        deployment=Deployment(status=Status.NotDeployed, message=""),
    )
    if auth_info:
        workspace.authInformation = auth_info
    return workspace


def create_sample_workspace_service_object(workspace_service_id, workspace_id):
    workspace_service = WorkspaceService(
        id=workspace_service_id,
        workspaceId=workspace_id,
        description="My workspace",
        resourceTemplateName="tre-workspace-vanilla",
        resourceTemplateVersion="0.1.0",
        resourceTemplateParameters={},
        deployment=Deployment(status=Status.NotDeployed, message=""),
    )

    return workspace_service


def create_sample_workspace_service_input_data():
    return {
        "workspaceServiceType": "test-workspace-service",
        "properties": {
            "display_name": "display",
            "app_id": "f0acf127-a672-a672-a672-a15e5bf9f127"
        }
    }


def create_sample_workspace_input_data():
    return {
        "workspaceType": "test-workspace",
        "properties": {
            "display_name": "display",
            "app_id": "f0acf127-a672-a672-a672-a15e5bf9f127"
        }
    }


# [GET] /workspaces
@ patch("api.routes.workspaces.WorkspaceRepository.get_all_active_workspaces")
async def test_workspaces_get_empty_list_when_no_resources_exist(get_workspaces_mock, app: FastAPI, client: AsyncClient) -> None:
    get_workspaces_mock.return_value = []

    response = await client.get(app.url_path_for(strings.API_GET_ALL_WORKSPACES))
    assert response.json() == {"workspaces": []}


# [GET] /workspaces
@ patch("api.routes.workspaces.WorkspaceRepository.get_all_active_workspaces")
async def test_workspaces_get_list_returns_correct_data_when_resources_exist(get_workspaces_mock, app: FastAPI, client: AsyncClient) -> None:
    auth_info_user_in_workspace_owner_role = {'sp_id': 'ab123', 'roles': {'WorkspaceOwner': 'ab124', 'WorkspaceResearcher': 'ab125'}}
    auth_info_user_not_in_workspace_role = {'sp_id': 'ab127', 'roles': {'WorkspaceOwner': 'ab128', 'WorkspaceResearcher': 'ab129'}}

    valid_ws_1 = create_sample_workspace_object("2fdc9fba-726e-4db6-a1b8-9018a2165748", auth_info_user_in_workspace_owner_role)
    valid_ws_2 = create_sample_workspace_object("000000d3-82da-4bfc-b6e9-9a7853ef753e", auth_info_user_in_workspace_owner_role)
    invalid_ws = create_sample_workspace_object("00000045-82da-4bfc-b6e9-9a7853ef7534", auth_info_user_not_in_workspace_role)

    get_workspaces_mock.return_value = [valid_ws_1, valid_ws_2, invalid_ws]

    response = await client.get(app.url_path_for(strings.API_GET_ALL_WORKSPACES))
    workspaces_from_response = response.json()["workspaces"]

    assert len(workspaces_from_response) == 2
    assert valid_ws_1 in workspaces_from_response
    assert valid_ws_2 in workspaces_from_response


# [GET] /workspaces/{workspace_id}
@ patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_workspace_id")
async def test_workspaces_id_get_returns_404_if_resource_is_not_found(get_workspace_mock, app: FastAPI, client: AsyncClient):
    get_workspace_mock.side_effect = EntityDoesNotExist

    response = await client.get(app.url_path_for(strings.API_GET_WORKSPACE_BY_ID, workspace_id="000000d3-82da-4bfc-b6e9-9a7853ef753e"))
    assert response.status_code == status.HTTP_404_NOT_FOUND


# [GET] /workspaces/{workspace_id}
@ patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_workspace_id")
async def test_workspaces_id_get_returns_422_if_workspace_id_is_not_a_uuid(get_workspace_mock, app: FastAPI, client: AsyncClient):
    get_workspace_mock.side_effect = EntityDoesNotExist

    response = await client.get(app.url_path_for(strings.API_GET_WORKSPACE_BY_ID, workspace_id="not_valid"))
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# [GET] /workspaces/{workspace_id}
@ patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_workspace_id")
async def test_workspaces_id_get_returns_workspace_if_found(get_workspace_mock, app: FastAPI, client: AsyncClient):
    workspace_id = "933ad738-7265-4b5f-9eae-a1a62928772e"
    auth_info_user_in_workspace_owner_role = {'sp_id': 'ab123', 'roles': {'WorkspaceOwner': 'ab124', 'WorkspaceResearcher': 'ab125'}}
    sample_workspace = create_sample_workspace_object(workspace_id, auth_info_user_in_workspace_owner_role)
    get_workspace_mock.return_value = sample_workspace

    response = await client.get(app.url_path_for(strings.API_GET_WORKSPACE_BY_ID, workspace_id=workspace_id))
    actual_resource = response.json()["workspace"]
    assert actual_resource["id"] == sample_workspace.id


# [POST] /workspaces/
@ patch("api.routes.workspaces.send_resource_request_message")
@ patch("api.routes.workspaces.WorkspaceRepository.save_workspace")
@ patch("api.routes.workspaces.WorkspaceRepository.create_workspace_item")
async def test_workspaces_post_creates_workspace(create_workspace_item_mock, save_workspace_mock, send_resource_request_message_mock, app: FastAPI, client: AsyncClient, admin_user: User):
    app.dependency_overrides[get_current_user] = admin_user
    workspace_id = "000000d3-82da-4bfc-b6e9-9a7853ef753e"
    create_workspace_item_mock.return_value = create_sample_workspace_object(workspace_id)
    input_data = create_sample_workspace_input_data()

    response = await client.post(app.url_path_for(strings.API_CREATE_WORKSPACE), json=input_data)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["workspaceId"] == workspace_id


# [POST] /workspaces/
@ patch("api.routes.workspaces.send_resource_request_message")
@ patch("api.routes.workspaces.WorkspaceRepository.save_workspace")
@ patch("api.routes.workspaces.WorkspaceRepository.create_workspace_item")
@ patch("api.routes.workspaces.WorkspaceRepository._validate_workspace_parameters")
async def test_workspaces_post_calls_db_and_service_bus(validate_workspace_parameters_mock, create_workspace_item_mock, save_workspace_mock, send_resource_request_message_mock, app: FastAPI, client: AsyncClient, admin_user: User):
    app.dependency_overrides[get_current_user] = admin_user
    workspace_id = "000000d3-82da-4bfc-b6e9-9a7853ef753e"
    validate_workspace_parameters_mock.return_value = None
    create_workspace_item_mock.return_value = create_sample_workspace_object(workspace_id)
    input_data = create_sample_workspace_input_data()

    await client.post(app.url_path_for(strings.API_CREATE_WORKSPACE), json=input_data)

    save_workspace_mock.assert_called_once()
    send_resource_request_message_mock.assert_called_once()


# [POST] /workspaces/{workspace_id}/services
@ patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_workspace_id")
@ patch("api.routes.workspaces.send_resource_request_message")
@ patch("api.routes.workspaces.WorkspaceServiceRepository.save_workspace_service")
@ patch("api.routes.workspaces.WorkspaceServiceRepository.create_workspace_service_item")
async def test_workspace_services_post_creates_workspace_service(create_workspace_service_item_mock, save_workspace_service_mock, send_resource_request_message_mock, get_workspace_mock, app: FastAPI, client: AsyncClient, admin_user: User):
    workspace_id = "98b8799a-7281-4fc5-91d5-49684a4810ff"
    auth_info_user_in_workspace_owner_role = {'sp_id': 'ab123',
                                              'roles': {'WorkspaceOwner': 'ab124', 'WorkspaceResearcher': 'ab125'}}
    sample_workspace = create_sample_workspace_object(workspace_id, auth_info_user_in_workspace_owner_role)
    get_workspace_mock.return_value = sample_workspace

    workspace_service_id = "000000d3-82da-4bfc-b6e9-9a7853ef753e"
    create_workspace_service_item_mock.return_value = create_sample_workspace_service_object(workspace_service_id, workspace_id)
    input_data = create_sample_workspace_service_input_data()

    response = await client.post(app.url_path_for(strings.API_CREATE_WORKSPACE_SERVICE, workspace_id=workspace_id), json=input_data)
    print(app.url_path_for(strings.API_CREATE_WORKSPACE_SERVICE, workspace_id=workspace_id))
    print(response.json())
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["workspaceServiceId"] == workspace_service_id


# [POST] /workspaces/
@ patch("api.routes.workspaces.send_resource_request_message")
@ patch("api.routes.workspaces.WorkspaceRepository.save_workspace")
@ patch("api.routes.workspaces.WorkspaceRepository.create_workspace_item")
@ patch("api.routes.workspaces.WorkspaceRepository._validate_workspace_parameters")
async def test_workspaces_post_returns_202_on_successful_create(validate_workspace_parameters_mock, create_workspace_item_mock, save_workspace_mock, send_resource_request_message_mock, app: FastAPI, client: AsyncClient, admin_user: User):
    app.dependency_overrides[get_current_user] = admin_user
    workspace_id = "000000d3-82da-4bfc-b6e9-9a7853ef753e"
    validate_workspace_parameters_mock.return_value = None
    create_workspace_item_mock.return_value = create_sample_workspace_object(workspace_id)
    input_data = create_sample_workspace_input_data()

    response = await client.post(app.url_path_for(strings.API_CREATE_WORKSPACE), json=input_data)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["workspaceId"] == workspace_id


# [POST] /workspaces/
@ patch("service_bus.resource_request_sender.send_resource_request_message")
@ patch("api.routes.workspaces.WorkspaceRepository.save_workspace")
@ patch("api.routes.workspaces.WorkspaceRepository.create_workspace_item")
@ patch("api.routes.workspaces.WorkspaceRepository._validate_workspace_parameters")
async def test_workspaces_post_returns_503_if_service_bus_call_fails(validate_workspace_parameters_mock, create_workspace_item_mock, save_workspace_mock, send_resource_request_message_mock, app: FastAPI, client: AsyncClient, admin_user: User):
    app.dependency_overrides[get_current_user] = admin_user
    workspace_id = "000000d3-82da-4bfc-b6e9-9a7853ef753e"
    validate_workspace_parameters_mock.return_value = None
    create_workspace_item_mock.return_value = create_sample_workspace_object(workspace_id)
    input_data = create_sample_workspace_input_data()

    send_resource_request_message_mock.side_effect = Exception

    response = await client.post(app.url_path_for(strings.API_CREATE_WORKSPACE), json=input_data)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


# [POST] /workspaces/
@ patch("api.routes.workspaces.WorkspaceRepository._get_current_workspace_template")
@ patch("api.routes.workspaces.WorkspaceRepository._validate_workspace_parameters")
async def test_workspaces_post_returns_400_if_template_does_not_exist(validate_workspace_parameters_mock, get_current_workspace_template_mock, app: FastAPI, client: AsyncClient, admin_user: User):
    app.dependency_overrides[get_current_user] = admin_user
    validate_workspace_parameters_mock.return_value = None
    get_current_workspace_template_mock.side_effect = EntityDoesNotExist
    input_data = create_sample_workspace_input_data()

    response = await client.post(app.url_path_for(strings.API_CREATE_WORKSPACE), json=input_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# [PATCH] /workspaces/{workspace_id}
@ patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_workspace_id")
async def test_workspaces_patch_returns_400_if_workspace_does_not_exist(get_workspace_mock, app: FastAPI, client: AsyncClient, admin_user: User):
    app.dependency_overrides[get_current_user] = admin_user

    get_workspace_mock.side_effect = EntityDoesNotExist
    workspace_id = "933ad738-7265-4b5f-9eae-a1a62928772e"

    input_data = '{"enabled": true}'

    response = await client.patch(app.url_path_for(strings.API_UPDATE_WORKSPACE, workspace_id=workspace_id), json=input_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
