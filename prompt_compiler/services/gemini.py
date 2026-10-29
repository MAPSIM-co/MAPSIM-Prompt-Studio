"""Google AI Studio HTTP integration."""

import json

import httpx

from ..config import effective_api_key


async def call_gemini(config, system_prompt, user_prompt, model_id):
    api_key = effective_api_key(config)
    if not api_key:
        raise ValueError(
            "کلید Google AI Studio تنظیم نشده است. از بخش تنظیمات آن را وارد کنید "
            "(https://aistudio.google.com/apikey)."
        )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{
            "role": "user",
            "parts": [{"text": (
                "Compile the following Persian request into an optimized English prompt. "
                "The English prompt is the canonical result. Then translate that exact finalized "
                "English prompt into a faithful Persian version. Do not generate Persian "
                "independently from the original input. Follow your instructions:\n\n"
                f"{user_prompt}"
            )}],
        }],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192},
    }

    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            url,
            # The key travels in a header: a query string lands in proxy and
            # access logs, which is not acceptable for a credential.
            headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
            json=payload,
        )

    if response.status_code != 200:
        content_type = response.headers.get("content-type", "").lower()
        response_text = response.text or ""
        if "html" in content_type or response_text.lstrip().lower().startswith("<!doctype"):
            raise ValueError(
                "سرویس Google درخواست را رد کرد (HTTP 403). دسترسی این شبکه به "
                "generativelanguage.googleapis.com را بررسی کنید."
            )
        try:
            error_data = response.json()
            error = error_data["error"]
            code = error.get("code", response.status_code)
            message = error.get("message", str(error))
        except (json.JSONDecodeError, KeyError, TypeError):
            code = response.status_code
            message = (response_text.strip()[:400]
                       or "پاسخ معتبر JSON از سرویس دریافت نشد.")
        if "api key" in message.lower() and "not valid" in message.lower():
            message = "کلید API معتبر نیست. از aistudio.google.com/apikey کلید تازه‌ای بسازید."
        raise ValueError(f"[{code}] {message}")

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise ValueError(
            "پاسخ معتبری از سرویس دریافت نشد (status="
            f"{response.status_code}): "
            f"{response.text.strip()[:400] if response.text else 'پاسخ خالی'}"
        ) from exc

    if "error" in data:
        error = data["error"]
        code = error.get("code", response.status_code)
        message = error.get("message", str(error))
        raise ValueError(f"[{code}] {message}")

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(
            "پاسخی از مدل بازنگشت: " + json.dumps(data, ensure_ascii=False)[:600]
        ) from exc

    return text, data.get("usageMetadata", {})
