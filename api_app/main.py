import asyncio
import logging
import uvicorn

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager

from starlette.exceptions import HTTPException
from starlette.middleware.errors import ServerErrorMiddleware

from api.routes.api import router as api_router
from api.errors.http_error import http_error_handler
from api.errors.validation_error import http422_error_handler
from api.errors.generic_error import generic_error_handler
from core import config
from db.events import bootstrap_database
from services.logging import initialize_logging
from service_bus.deployment_status_updater import DeploymentStatusUpdater
from service_bus.airlock_request_status_update import AirlockStatusUpdater


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cosmos_client = None

    while not await bootstrap_database(app):
        await asyncio.sleep(5)
        logging.warning("Database connection could not be established")

    deploymentStatusUpdater = DeploymentStatusUpdater(app)
    await deploymentStatusUpdater.init_repos()

    airlockStatusUpdater = AirlockStatusUpdater(app)
    await airlockStatusUpdater.init_repos()

    asyncio.create_task(deploymentStatusUpdater.receive_messages())
    asyncio.create_task(airlockStatusUpdater.receive_messages())
    yield


logger = logging.getLogger()


def get_application() -> FastAPI:
    application = FastAPI(
        title=config.PROJECT_NAME,
        debug=config.DEBUG,
        description=config.API_DESCRIPTION,
        version=config.VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None
    )

    if config.DEBUG:
        initialize_logging(logging.DEBUG, True, application)
    else:
        initialize_logging(logging.INFO, False, application)

    application.add_middleware(ServerErrorMiddleware, handler=generic_error_handler)

    # Allow local UI debugging with local API
    if config.ENABLE_LOCAL_DEBUGGING:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"])

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(api_router)
    return application


app = get_application()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio")
