import pytest

from httpx import AsyncClient
from starlette import status

import config
from helpers import get_auth_header, get_template
from resources import strings
from conftest import admin_token

shared_service_templates = [
    (strings.FIREWALL_SHARED_SERVICE),
    (strings.GITEA_SHARED_SERVICE),
]


@pytest.mark.smoke
@pytest.mark.parametrize("template_name", shared_service_templates)
async def test_get_shared_service_templates(template_name, verify) -> None:
    async with AsyncClient(verify=verify) as client:
        admin_tkn = admin_token(verify)
        response = await client.get(f"https://{config.TRE_ID}.{config.RESOURCE_LOCATION}.cloudapp.azure.com{strings.API_SHARED_SERVICE_TEMPLATES}", headers=get_auth_header(admin_tkn))

        template_names = [templates["name"] for templates in response.json()["templates"]]
        assert (template_name in template_names), f"No {template_name} template found"


@pytest.mark.smoke
@pytest.mark.parametrize("template_name", shared_service_templates)
async def test_get_shared_service_template(template_name, verify) -> None:
    admin_tkn = admin_token(verify)
    async with get_template(template_name, strings.API_SHARED_SERVICE_TEMPLATES, admin_tkn, verify) as response:
        assert (response.status_code == status.HTTP_200_OK), f"GET Request for {template_name} failed"
