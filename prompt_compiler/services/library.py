"""Local prompt library: saved compilations with tags, favorites and search.

Everything lives in one JSON file next to ``config.json``. The library holds the
operator's own requests and prompts, so it is written with owner-only
permissions and through a temporary file.
"""

import json
import os
import re
import time
import uuid

from ..config import LIBRARY_FILE
from ..prompt_engine import mirror_analysis


#: The file is a working set, not an archive: the oldest entries are dropped
#: past this limit so a long-running studio never grows without bound.
MAX_ENTRIES = 500

TITLE_LENGTH = 90
TAG_LIMIT = 12
SEARCH_LIMIT = 100

#: A request longer than this is a paste error, not a prompt. The same guard is
#: reused by the compile endpoint so nothing oversized reaches the provider.
MAX_INPUT_LENGTH = 20_000

_TAG_CLEAN = re.compile(r"[^\w\u0600-\u06FF-]+")


def _title_from(text):
    collapsed = " ".join((text or "").split())
    if len(collapsed) <= TITLE_LENGTH:
        return collapsed
    return collapsed[:TITLE_LENGTH].rstrip() + "…"


def normalize_tag(tag):
    """Lower-case a tag and keep letters, digits, Persian letters and dashes."""
    cleaned = _TAG_CLEAN.sub("-", str(tag or "").strip().lower()).strip("-")
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    return cleaned[:40]


def load_library():
    if LIBRARY_FILE.exists():
        try:
            with LIBRARY_FILE.open("r", encoding="utf-8") as library_file:
                data = json.load(library_file)
        except (OSError, json.JSONDecodeError):
            return []
        entries = data.get("entries", []) if isinstance(data, dict) else data
        return entries if isinstance(entries, list) else []
    return []


def save_library(entries):
    temporary = LIBRARY_FILE.with_suffix(".json.tmp")
    with temporary.open("w", encoding="utf-8") as library_file:
        json.dump({"entries": entries[:MAX_ENTRIES]}, library_file, ensure_ascii=False, indent=2)
    os.replace(temporary, LIBRARY_FILE)
    try:
        os.chmod(LIBRARY_FILE, 0o600)
    except OSError:
        pass


#: The four analysis groups, stored in both languages so a loaded entry can
#: refill the Persian and English halves of the result card.
ANALYSIS_GROUPS = ("preserved_requirements", "assumptions", "missing_information", "suggestions")


def _analysis_block(source):
    """Copy one language's analysis out of a compile result, defensively."""
    block = source if isinstance(source, dict) else {}
    analysis = {"detected_purpose": str(block.get("detected_purpose") or "")}
    for key in ANALYSIS_GROUPS:
        analysis[key] = [str(item) for item in (block.get(key) or []) if str(item).strip()]
    return analysis


def create_entry(payload):
    """Build a stored entry from a compile result; empty input is rejected."""
    source_text = str(payload.get("input", "") or "").strip()
    if not source_text:
        raise ValueError("یک درخواست فارسی برای ذخیره‌شدن لازم است.")

    parsed = payload.get("parsed") or {}
    tags = [normalize_tag(tag) for tag in (payload.get("tags") or [])]
    category = normalize_tag(parsed.get("detected_category"))
    if category and category not in tags:
        tags.append(category)
    tags = [tag for tag in dict.fromkeys(tags) if tag][:TAG_LIMIT]

    return {
        "id": uuid.uuid4().hex[:12],
        "created_at": int(time.time() * 1000),
        "title": str(payload.get("title") or "").strip() or _title_from(source_text),
        "input": source_text,
        "model": str(payload.get("model", "") or ""),
        "category": parsed.get("detected_category", "") or "",
        "subcategory": parsed.get("detected_subcategory", "") or "",
        "purpose": parsed.get("detected_purpose", "") or "",
        "english_prompt": parsed.get("english_prompt", "") or "",
        "persian_prompt": parsed.get("persian_prompt", "") or "",
        "preserved_requirements": list(parsed.get("preserved_requirements") or []),
        "assumptions": list(parsed.get("assumptions") or []),
        "missing_information": list(parsed.get("missing_information") or []),
        "suggestions": list(parsed.get("suggestions") or []),
        "persian_analysis": mirror_analysis(
            _analysis_block(parsed.get("persian_analysis")), parsed
        ),
        "tags": tags,
        "favorite": bool(payload.get("favorite")),
    }


def add_entry(payload):
    entry = create_entry(payload)
    entries = load_library()
    entries.insert(0, entry)
    save_library(entries)
    return entry


def find_entry(entry_id):
    for entry in load_library():
        if entry.get("id") == entry_id:
            return entry
    return None


#: What the library editor is allowed to rewrite. The long text fields are the
#: reason the editor exists: a stored request nobody can correct is dead weight.
EDITABLE_FIELDS = (
    "title", "tags", "favorite",
    "input", "purpose", "persian_prompt", "english_prompt",
)


def update_entry(entry_id, changes):
    """Apply the editor's changes and return the stored entry."""
    entry = find_entry(entry_id)
    if entry is None:
        return None

    previous_input = entry.get("input", "")
    if "input" in changes:
        text = str(changes.get("input") or "").strip()
        if not text:
            raise ValueError("متن درخواست نمی‌تواند خالی بماند.")
        if len(text) > MAX_INPUT_LENGTH:
            raise ValueError(f"درخواست خیلی بلند است؛ حداکثر {MAX_INPUT_LENGTH} نویسه.")
        entry["input"] = text
        # An auto-derived title follows the request; a hand-written one stays.
        if entry.get("title", "") == _title_from(previous_input):
            entry["title"] = _title_from(text)

    for key in ("purpose", "persian_prompt", "english_prompt"):
        if key in changes:
            entry[key] = str(changes.get(key) or "").strip()

    if "title" in changes:
        title = str(changes.get("title") or "").strip()
        entry["title"] = title or _title_from(entry.get("input", ""))
    if "favorite" in changes:
        entry["favorite"] = bool(changes.get("favorite"))
    if "tags" in changes:
        tags = [normalize_tag(tag) for tag in (changes.get("tags") or [])]
        entry["tags"] = [tag for tag in dict.fromkeys(tags) if tag][:TAG_LIMIT]

    entries = load_library()
    save_library([entry if item.get("id") == entry_id else item for item in entries])
    return entry


def delete_entry(entry_id):
    entries = load_library()
    kept = [entry for entry in entries if entry.get("id") != entry_id]
    if len(kept) == len(entries):
        return False
    save_library(kept)
    return True


def tag_counts(entries=None):
    entries = load_library() if entries is None else entries
    counts = {}
    for entry in entries:
        for tag in entry.get("tags") or []:
            counts[tag] = counts.get(tag, 0) + 1
    return [{"tag": tag, "count": count} for tag, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]


def _text_list(value):
    """Join a stored list of strings, ignoring anything that is not a string."""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return " ".join(str(item) for item in value if isinstance(item, str))
    return ""


def matches(entry, needle):
    analysis = entry.get("persian_analysis")
    analysis = analysis if isinstance(analysis, dict) else {}
    haystack = " ".join([
        entry.get("title", ""),
        entry.get("input", ""),
        entry.get("english_prompt", ""),
        entry.get("persian_prompt", ""),
        entry.get("purpose", ""),
        _text_list(analysis.get("detected_purpose")),
        " ".join(_text_list(analysis.get(key)) for key in ANALYSIS_GROUPS),
        " ".join(_text_list(entry.get(key)) for key in ANALYSIS_GROUPS),
        " ".join(entry.get("tags") or []),
    ]).lower()
    return needle in haystack


def search(query="", tag="", favorite_only=False, limit=SEARCH_LIMIT):
    """Filter the library newest-first; tag matches exactly, text is a substring."""
    entries = load_library()
    needle = (query or "").strip().lower()
    wanted_tag = normalize_tag(tag)

    if wanted_tag:
        entries = [entry for entry in entries if wanted_tag in (entry.get("tags") or [])]
    if favorite_only:
        entries = [entry for entry in entries if entry.get("favorite")]
    if needle:
        entries = [entry for entry in entries if matches(entry, needle)]

    return entries[:max(1, min(int(limit or SEARCH_LIMIT), MAX_ENTRIES))]
