"""Application configuration, project paths and API-key handling.

The API key is a secret: it is read from the environment when available, stored
with owner-only permissions, and never handed to a template.
"""

import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.json"
USAGE_FILE = PROJECT_ROOT / "usage.json"
LIBRARY_FILE = PROJECT_ROOT / "library.json"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"

DEFAULT_MODEL = "gemini-3.5-flash"

#: Checked in order; an environment key wins over the stored one so the same
#: build works on a shared machine without writing secrets to disk.
API_KEY_ENV_VARS = ("PROMPT_STUDIO_API_KEY", "GEMINI_API_KEY")

#: Sentinel a settings form sends to delete the stored key.
CLEAR_API_KEY = "__CLEAR__"

DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "gemini_model": DEFAULT_MODEL,
    "system_prompt_override": "",
}


def load_config():
    """Load persisted settings, falling back to safe defaults on bad input."""
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as config_file:
                data = json.load(config_file)
        except (OSError, json.JSONDecodeError):
            return dict(DEFAULT_CONFIG)
        return {
            "gemini_api_key": str(data.get("gemini_api_key", "") or ""),
            "gemini_model": data.get("gemini_model") or DEFAULT_MODEL,
            "system_prompt_override": data.get("system_prompt_override", ""),
        }
    return dict(DEFAULT_CONFIG)


def save_config(config):
    """Persist settings with owner-only permissions.

    Written through a temporary file so a crash cannot leave a half-written
    config behind.
    """
    payload = {
        "gemini_api_key": str(config.get("gemini_api_key", "") or ""),
        "gemini_model": config.get("gemini_model") or DEFAULT_MODEL,
        "system_prompt_override": config.get("system_prompt_override", ""),
    }
    temporary = CONFIG_FILE.with_suffix(".json.tmp")
    with temporary.open("w", encoding="utf-8") as config_file:
        json.dump(payload, config_file, indent=2, ensure_ascii=False)
    os.replace(temporary, CONFIG_FILE)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass
    return payload


def env_api_key():
    """Return an API key supplied through the environment, if any."""
    for name in API_KEY_ENV_VARS:
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    return ""


def effective_api_key(config=None):
    """The key actually used for a request: environment first, then storage."""
    from_environment = env_api_key()
    if from_environment:
        return from_environment
    return (config or load_config()).get("gemini_api_key", "")


def mask_api_key(key):
    """A display-safe hint that never reveals more than the last four chars."""
    key = (key or "").strip()
    if not key:
        return ""
    return "••••••••" + key[-4:]


def public_config(config=None):
    """Settings shaped for the template: no secret ever reaches the browser."""
    config = config or load_config()
    from_environment = env_api_key()
    stored_key = config.get("gemini_api_key", "")
    return {
        "gemini_model": config.get("gemini_model") or DEFAULT_MODEL,
        "system_prompt_override": config.get("system_prompt_override", ""),
        "has_api_key": bool(from_environment or stored_key),
        "api_key_masked": mask_api_key(from_environment or stored_key),
        "api_key_source": "environment" if from_environment else ("stored" if stored_key else ""),
    }
