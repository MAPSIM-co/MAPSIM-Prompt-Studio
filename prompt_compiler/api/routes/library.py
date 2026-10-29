"""Prompt library endpoints: save, browse, tag and delete compilations."""

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from ...services.library import (
    EDITABLE_FIELDS,
    MAX_INPUT_LENGTH,
    add_entry,
    delete_entry,
    load_library,
    search,
    tag_counts,
    update_entry,
)


router = APIRouter()


def _bad_request(message, status_code=400):
    return JSONResponse({"error": message}, status_code=status_code)


@router.get("/library")
async def list_library(
    q: str = Query(""),
    tag: str = Query(""),
    favorite: bool = Query(False),
    limit: int = Query(100, ge=1, le=500),
):
    try:
        entries = search(query=q, tag=tag, favorite_only=favorite, limit=limit)
    except ValueError as exc:
        return _bad_request(str(exc))
    return JSONResponse({
        "entries": entries,
        "tags": tag_counts(),
        "total": len(load_library()),
        "returned": len(entries),
    })


@router.post("/library", status_code=201)
async def save_library_entry(request: Request):
    try:
        body = await request.json()
    except Exception:
        return _bad_request("بدنه درخواست معتبر نیست")

    if not isinstance(body, dict):
        return _bad_request("بدنه درخواست معتبر نیست")
    if len(str(body.get("input", "") or "")) > MAX_INPUT_LENGTH:
        return _bad_request(f"درخواست خیلی بلند است؛ حداکثر {MAX_INPUT_LENGTH} نویسه.")

    try:
        entry = add_entry(body)
    except ValueError as exc:
        return _bad_request(str(exc))
    return JSONResponse({"entry": entry}, status_code=201)


@router.patch("/library/{entry_id}")
async def edit_library_entry(entry_id: str, request: Request):
    try:
        body = await request.json()
    except Exception:
        return _bad_request("بدنه درخواست معتبر نیست")

    if not isinstance(body, dict):
        return _bad_request("بدنه درخواست معتبر نیست")

    allowed = {key: body[key] for key in EDITABLE_FIELDS if key in body}
    try:
        entry = update_entry(entry_id, allowed)
    except ValueError as exc:
        return _bad_request(str(exc))
    if entry is None:
        return _bad_request("چنین موردی در کتابخانه نیست", status_code=404)
    return JSONResponse({"entry": entry})


@router.delete("/library/{entry_id}")
async def remove_library_entry(entry_id: str):
    if not delete_entry(entry_id):
        return _bad_request("چنین موردی در کتابخانه نیست", status_code=404)
    return JSONResponse({"status": "deleted", "id": entry_id})
