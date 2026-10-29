"""FastAPI application factory and router registration."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.routes import library, models, pages, settings, translation, usage
from .config import STATIC_DIR


def create_app():
    application = FastAPI(
        title="MAPSIM Prompt Studio",
        description="MAPSIM Persian-to-English prompt engineering workspace",
        version="2.2.0",
    )
    application.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    application.include_router(pages.router)
    application.include_router(models.router)
    application.include_router(usage.router)
    application.include_router(settings.router)
    application.include_router(translation.router)
    application.include_router(library.router)
    return application


app = create_app()
