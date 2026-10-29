"""HTML page routes."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ...catalog import MODELS
from ...config import TEMPLATES_DIR, public_config


router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def model_choices():
    """Split the catalog into what this app can compile with and the rest."""
    usable = [model for model in MODELS if model["generate"]]
    unusable = [model for model in MODELS if not model["generate"]]
    return usable, unusable


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    usable, unusable = model_choices()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "config": public_config(),
            "usable_models": usable,
            "unusable_models": unusable,
        },
    )
