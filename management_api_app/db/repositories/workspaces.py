import uuid
from typing import List

from azure.cosmos import ContainerProxy, CosmosClient

from core.config import STATE_STORE_RESOURCES_CONTAINER
from db.errors import EntityDoesNotExist, UnableToAccessDatabase
from db.query_builder import QueryBuilder
from db.repositories.base import BaseRepository
from models.domain.resource import Resource, ResourceSpec, ResourceType, Status
from models.schemas.resource import ResourceInCreate


class WorkspaceRepository(BaseRepository):
    def __init__(self, client: CosmosClient):
        super().__init__(client, STATE_STORE_RESOURCES_CONTAINER)

    @property
    def container(self) -> ContainerProxy:
        return self._container

    def get_all_active_workspaces(self) -> List[Resource]:
        try:
            query = QueryBuilder().select_active_resources(ResourceType.Workspace).build()
            workspaces = list(self.container.query_items(query=query, enable_cross_partition_query=True))
            return workspaces
        except Exception:
            raise UnableToAccessDatabase

    def get_workspace_by_workspace_id(self, workspace_id: str) -> Resource:
        try:
            query = QueryBuilder().select_active_resources(ResourceType.Workspace).with_id(workspace_id).build()
            workspaces = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        except Exception:
            raise UnableToAccessDatabase

        if workspaces:
            return workspaces[0]
        else:
            raise EntityDoesNotExist

    def create_workspace(self, workspace_create: ResourceInCreate) -> Resource:
        try:
            workspace = Resource(
                id=str(uuid.uuid4()),
                resourceSpec=ResourceSpec(name=workspace_create.resourceSpec.name, version=workspace_create.resourceSpec.version),
                parameters=workspace_create.parameters,
                resourceType=ResourceType.Workspace,
                status=Status.NotDeployed
            )
            self.container.create_item(body=workspace.dict())
            return workspace
        except Exception:
            raise UnableToAccessDatabase
