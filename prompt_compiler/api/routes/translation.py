"""Prompt translation/compilation endpoint."""

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ...catalog import DEFAULT_MODEL, MODELS
from ...config import load_config
from ...prompt_engine import SYSTEM_PROMPT, parse_model_output
from ...services.gemini import call_gemini
from ...services.library import MAX_INPUT_LENGTH
from ...services.usage import record_usage


router = APIRouter()


@router.post("/translate")
async def translate(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "درخواست نامعتبر است؛ دوباره تلاش کنید."}, status_code=400)

    persian_text = body.get("prompt", "")
    if not isinstance(persian_text, str):
        return JSONResponse({"error": "متن درخواست باید نوشته باشد."}, status_code=400)

    model_id = (body.get("model", "") or "").strip()
    config = load_config()

    if not persian_text.strip():
        return JSONResponse({"error": "متن درخواست خالی است؛ ابتدا درخواست خود را بنویسید."}, status_code=400)

    if len(persian_text) > MAX_INPUT_LENGTH:
        return JSONResponse(
            {"error": f"درخواست از {MAX_INPUT_LENGTH:,} نویسه بیشتر است؛ آن را کوتاه‌تر کنید."},
            status_code=413,
        )

    if not model_id:
        model_id = config.get("gemini_model", DEFAULT_MODEL)

    model = next((item for item in MODELS if item["id"] == model_id), None)
    if model is not None and not model.get("generate"):
        reason = model.get("unusable_fa", "این مدل پرامپت متنی تولید نمی‌کند.")
        return JSONResponse(
            {"error": f"مدل «{model['name']}» برای تبدیل استفاده نمی‌شود: {reason}. "
                      "از فهرست مدل‌های قابل استفاده یکی را انتخاب کنید."},
            status_code=400,
        )

    system_prompt = config.get("system_prompt_override", "") or SYSTEM_PROMPT

    try:
        text, usage = await call_gemini(config, system_prompt, persian_text, model_id)
        record_usage(model_id, usage)
        return JSONResponse({
            "result": text,
            "parsed": parse_model_output(text),
            "usage": usage,
            "model": model_id,
        })
    except httpx.HTTPError as exc:
        return JSONResponse(
            {
                "error": (
                    "اتصال به سرویس Google AI Studio برقرار نشد "
                    f"({type(exc).__name__}). دسترسی شبکه به generativelanguage.googleapis.com را بررسی کنید."
                )
            },
            status_code=500,
        )
    except Exception as exc:
        return JSONResponse({"error": f"خطای غیرمنتظره: {exc}"}, status_code=500)
