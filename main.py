"""Entry point for the refactored Prompt Compiler.

Binds to the loopback address by default: this tool stores an API key and
personal prompts, so it must not be reachable from the local network unless the
operator opts in explicitly.
"""

import os

from prompt_compiler.app import app
from prompt_compiler.catalog import DEFAULT_MODEL, KNOWN_CATEGORIES, MODELS, group_models
from prompt_compiler.config import (
    CONFIG_FILE,
    LIBRARY_FILE,
    USAGE_FILE,
    effective_api_key,
    load_config,
    public_config,
    save_config,
)
from prompt_compiler.prompt_engine import SYSTEM_PROMPT, parse_model_output
from prompt_compiler.services.gemini import call_gemini
from prompt_compiler.services.usage import (
    compute_usage,
    load_usage,
    local_midnight_ms,
    record_usage,
    save_usage,
)

__all__ = [
    "app",
    "DEFAULT_MODEL",
    "KNOWN_CATEGORIES",
    "MODELS",
    "group_models",
    "CONFIG_FILE",
    "USAGE_FILE",
    "LIBRARY_FILE",
    "load_config",
    "save_config",
    "public_config",
    "effective_api_key",
    "SYSTEM_PROMPT",
    "parse_model_output",
    "call_gemini",
    "compute_usage",
    "load_usage",
    "local_midnight_ms",
    "record_usage",
    "save_usage",
]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.environ.get("PROMPT_STUDIO_HOST", "127.0.0.1"),
        port=int(os.environ.get("PROMPT_STUDIO_PORT", "8000")),
    )
