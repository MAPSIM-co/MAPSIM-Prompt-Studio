"""Settings endpoint.

An empty key field means "keep the key already stored" — the browser never sees
the stored value, so it cannot echo it back.
"""

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

from ...catalog import DEFAULT_MODEL
from ...config import (
    CLEAR_API_KEY,
    env_api_key,
    load_config,
    mask_api_key,
    save_config,
)


router = APIRouter()


@router.post("/settings")
async def update_settings(
    gemini_api_key: str = Form(""),
    gemini_model: str = Form(DEFAULT_MODEL),
    system_prompt_override: str = Form(""),
):
    stored = load_config()
    submitted = gemini_api_key.strip()
    if submitted == CLEAR_API_KEY:
        resolved_key = ""
    elif submitted:
        resolved_key = submitted
    else:
        resolved_key = stored.get("gemini_api_key", "")

    saved = save_config({
        "gemini_api_key": resolved_key,
        "gemini_model": gemini_model.strip() or DEFAULT_MODEL,
        "system_prompt_override": system_prompt_override,
    })

    environment_key = env_api_key()
    return JSONResponse({
        "status": "ok",
        "message": "تنظیمات ذخیره شد.",
        "has_api_key": bool(environment_key or saved["gemini_api_key"]),
        "api_key_masked": mask_api_key(environment_key or saved["gemini_api_key"]),
        "api_key_source": "environment" if environment_key else ("stored" if saved["gemini_api_key"] else ""),
        "gemini_model": saved["gemini_model"],
    })
