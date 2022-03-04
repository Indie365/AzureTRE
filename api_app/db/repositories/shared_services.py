import uuid
from typing import List

from azure.cosmos import CosmosClient
from pydantic import parse_obj_as
from db.repositories.resource_templates import ResourceTemplateRepository

from db.repositories.resources import ResourceRepository, IS_ACTIVE_CLAUSE
from models.domain.shared_service import SharedService
from models.schemas.resource import ResourcePatch
from models.schemas.shared_service_template import SharedServiceInCreate
from models.domain.resource import ResourceType


class SharedServiceRepository(ResourceRepository):
    def __init__(self, client: CosmosClient):
        super().__init__(client)

    @staticmethod
    def shared_services_query(shared_service_id: str):
        return f'SELECT * FROM c WHERE c.resourceType = "{ResourceType.SharedService}" AND c.sharedServiceId = "{shared_service_id}"'

    @staticmethod
    def active_shared_services_query(shared_service_id: str):
        return f'SELECT * FROM c WHERE {IS_ACTIVE_CLAUSE} AND c.resourceType = "{ResourceType.SharedService}" AND c.sharedId = "{shared_service_id}"'

    def get_active_shared_services_for_shared(self, shared_service_id: str) -> List[SharedService]:
        """
        returns list of "non-deleted" shared services linked to this shared
        """
        query = SharedServiceRepository.active_shared_services_query(shared_service_id)
        shared_services = self.query(query=query)
        return parse_obj_as(List[SharedService], shared_services)

    def get_shared_service_spec_params(self):
        return self.get_resource_base_spec_params()

    def create_shared_service_item(self, shared_service_input: SharedServiceInCreate, shared_service_id: str) -> SharedService:
        full_shared_service_id = str(uuid.uuid4())

        template_version = self.validate_input_against_template(shared_service_input.templateName, shared_service_input, ResourceType.SharedService)

        # we don't want something in the input to overwrite the system parameters, so dict.update can't work.
        resource_spec_parameters = {**shared_service_input.properties, **self.get_shared_service_spec_params()}

        shared_service = SharedService(
            sharedServiceIid=full_shared_service_id,
            templateName=shared_service_input.templateName,
            templateVersion=template_version,
            properties=resource_spec_parameters,
            resourcePath=f'/shareds/{shared_service_id}/shared-services/{full_shared_service_id}',
            etag=''
        )

        return shared_service

    def patch_shared_service(self, shared_service: SharedService, shared_service_patch: ResourcePatch, etag: str, resource_template_repo: ResourceTemplateRepository) -> SharedService:
        # get shared service template
        shared_service_template = resource_template_repo.get_template_by_name_and_version(shared_service.templateName, shared_service.templateVersion, ResourceType.SharedService)
        return self.patch_resource(shared_service, shared_service_patch, shared_service_template, etag)
