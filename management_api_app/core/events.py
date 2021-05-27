from typing import Callable

from fastapi import FastAPI

from db.events import close_db_connection, connect_to_db, bootstrap_database


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        await connect_to_db(app)
        await bootstrap_database(app)

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        await close_db_connection(app)

    return stop_app
