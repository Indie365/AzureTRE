import datetime
import uuid
import pytest
from mock import patch

from fastapi import status

from db.errors import EntityDoesNotExist
from models.domain.shared_service import SharedService
from resources import strings
from services.authentication import get_current_admin_user, get_current_tre_user_or_tre_admin
from azure.cosmos.exceptions import CosmosAccessConditionFailedError
from models.domain.resource import ResourceHistoryItem


pytestmark = pytest.mark.asyncio


SHARED_SERVICE_ID = 'abcad738-7265-4b5f-9eae-a1a62928772e'
FAKE_UPDATE_TIME = datetime.datetime(2022, 1, 1, 17, 5, 55)
FAKE_UPDATE_TIMESTAMP: float = FAKE_UPDATE_TIME.timestamp()


@pytest.fixture
def shared_service_input():
    return {
        "templateName": "test-shared-service",
        "properties": {
            "display_name": "display"
        }
    }


def sample_shared_service(shared_service_id=SHARED_SERVICE_ID):
    return SharedService(
        id=shared_service_id,
        templateName="tre-shared-service-base",
        templateVersion="0.1.0",
        etag="",
        properties={},
        resourcePath=f'/shared-services/{shared_service_id}'
    )


class TestSharedServiceRoutesThatDontRequireAdminRigths:
    @pytest.fixture(autouse=True, scope='class')
    def log_in_with_non_admin_user(self, app, non_admin_user):
        with patch('services.aad_authentication.AzureADAuthorization._get_user_from_token', return_value=non_admin_user()):
            app.dependency_overrides[get_current_tre_user_or_tre_admin] = non_admin_user
            yield
            app.dependency_overrides = {}

    # [GET] /shared-services
    @patch("api.routes.shared_services.SharedServiceRepository.get_active_shared_services",
           return_value=None)
    async def test_get_shared_services_returns_list_of_shared_services(self, get_active_shared_services_mock, app, client):
        shared_services = [sample_shared_service()]
        get_active_shared_services_mock.return_value = shared_services

        response = await client.get(app.url_path_for(strings.API_GET_ALL_SHARED_SERVICES))

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["sharedServices"][0]["id"] == sample_shared_service().id


class TestSharedServiceRoutesThatRequireAdminRights:
    @pytest.fixture(autouse=True, scope='class')
    def _prepare(self, app, admin_user):
        with patch('services.aad_authentication.AzureADAuthorization._get_user_from_token', return_value=admin_user()):
            app.dependency_overrides[get_current_tre_user_or_tre_admin] = admin_user
            app.dependency_overrides[get_current_admin_user] = admin_user
            yield
            app.dependency_overrides = {}

    # [GET] /shared-services/{shared_service_id}
    @patch("api.dependencies.shared_services.SharedServiceRepository.get_shared_service_by_id", return_value=sample_shared_service())
    async def test_get_shared_service_returns_shared_service_result(self, get_shared_service_mock, app, client):
        shared_service = sample_shared_service(shared_service_id=str(uuid.uuid4()))
        get_shared_service_mock.return_value = shared_service

        response = await client.get(
            app.url_path_for(strings.API_GET_SHARED_SERVICE_BY_ID, shared_service_id=SHARED_SERVICE_ID))

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["sharedService"]["id"] == shared_service.id

    # [GET] /shared-services/{shared_service_id}
    @patch("api.routes.shared_services.SharedServiceRepository.get_active_shared_services")
    @patch("api.dependencies.shared_services.SharedServiceRepository.get_shared_service_by_id", side_effect=EntityDoesNotExist)
    async def test_get_shared_service_raises_404_if_not_found(self, get_shared_service_mock, _,
                                                              app, client):
        get_shared_service_mock.return_value = sample_shared_service(SHARED_SERVICE_ID)

        response = await client.get(
            app.url_path_for(strings.API_GET_SHARED_SERVICE_BY_ID, shared_service_id=SHARED_SERVICE_ID))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    # [PATCH] /shared-services/{shared_service_id}
    @patch("api.dependencies.shared_services.SharedServiceRepository.get_shared_service_by_id", side_effect=EntityDoesNotExist)
    async def test_patch_shared_service_returns_404_if_does_not_exist(self, _, app, client):
        response = await client.patch(app.url_path_for(strings.API_UPDATE_SHARED_SERVICE, shared_service_id=SHARED_SERVICE_ID), json='{"enabled": true}')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # [PATCH] /shared-services/{shared_service_id}
    @patch("api.dependencies.shared_services.SharedServiceRepository.get_shared_service_by_id", return_value=sample_shared_service())
    @patch("api.dependencies.shared_services.SharedServiceRepository.patch_shared_service", side_effect=CosmosAccessConditionFailedError)
    async def test_patch_shared_service_returns_409_if_bad_etag(self, _, __, app, client):
        shared_service_patch = {"isEnabled": True}
        etag = "some-bad-etag-value"

        response = await client.patch(app.url_path_for(strings.API_UPDATE_SHARED_SERVICE, shared_service_id=SHARED_SERVICE_ID), json=shared_service_patch, headers={"etag": etag})
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.text == strings.ETAG_CONFLICT

    # [PATCH] /shared-services/{shared_service_id}
    @patch("api.dependencies.shared_services.SharedServiceRepository.get_shared_service_by_id", side_effect=EntityDoesNotExist)
    async def test_patch_shared_service_returns_422_if_invalid_id(self, get_shared_service_mock, app, client):
        shared_service_id = "IAmNotEvenAGUID!"
        get_shared_service_mock.return_value = sample_shared_service(shared_service_id)

        response = await client.patch(app.url_path_for(strings.API_UPDATE_SHARED_SERVICE, shared_service_id=shared_service_id), json={"enabled": True})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # [PATCH] /shared-services/{shared_service_id}
    @patch("api.dependencies.shared_services.SharedServiceRepository.get_shared_service_by_id", return_value=sample_shared_service())
    @patch("api.routes.shared_services.ResourceTemplateRepository.get_template_by_name_and_version", return_value=None)
    @patch("api.routes.shared_services.SharedServiceRepository.update_item_with_etag", return_value=sample_shared_service())
    @patch("api.routes.shared_services.SharedServiceRepository.get_timestamp", return_value=FAKE_UPDATE_TIMESTAMP)
    async def test_patch_workspace_service_patches_workspace_service(self, _, update_item_mock, __, get_shared_service_mock, app, client):
        get_shared_service_mock.return_value = sample_shared_service(SHARED_SERVICE_ID)
        etag = "some-etag-value"
        shared_service_patch = {"isEnabled": False}

        modified_shared_service = sample_shared_service()
        modified_shared_service.isEnabled = False
        modified_shared_service.history = [ResourceHistoryItem(properties={}, isEnabled=True, resourceVersion=0, updatedWhen=FAKE_UPDATE_TIMESTAMP)]
        modified_shared_service.resourceVersion = 1

        response = await client.patch(app.url_path_for(strings.API_UPDATE_SHARED_SERVICE, shared_service_id=SHARED_SERVICE_ID), json=shared_service_patch, headers={"etag": etag})
        update_item_mock.assert_called_once_with(modified_shared_service, etag)

        assert response.status_code == status.HTTP_200_OK
