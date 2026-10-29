#!/usr/bin/env bash
#
# MAPSIM Prompt Studio - one-command setup and launch (macOS, Linux, WSL, Git Bash).
#
#   ./run.sh                 create .venv, install dependencies, start the server
#   ./run.sh --port 8005     start on another port
#   ./run.sh --open          also open the page in the default browser
#   ./run.sh --tests         run the test suite instead of the server
#   ./run.sh --reload        development mode (restarts on file changes)
#
# Nothing here is interactive and nothing outside this project folder is touched:
# the virtual environment, the dependency install and the marker file all live in
# .venv/. An existing .venv is never deleted - if it is broken the script stops and
# tells you what to do instead of silently destroying your environment.

set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

readonly MIN_PYTHON_MINOR=10
readonly VENV_DIR=".venv"
readonly VENV_PY="$VENV_DIR/bin/python"
readonly REQ_FILE="requirements.txt"
readonly HASH_FILE="$VENV_DIR/.requirements.sha256"

HOST="${PROMPT_STUDIO_HOST:-127.0.0.1}"
PORT="${PROMPT_STUDIO_PORT:-8000}"
PYTHON_BIN="${PROMPT_STUDIO_PYTHON:-}"
RELOAD=0
RUN_TESTS=0
OPEN_BROWSER=0
PREPARE_ONLY=0

say() { printf '%b\n' "$*"; }
step() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
fail() { printf '\n\033[1;31m  ! %s\033[0m\n\n' "$*" >&2; exit 1; }

usage() {
    cat <<'HELP'
Usage: ./run.sh [options]

  --host ADDRESS   bind address (default 127.0.0.1, or PROMPT_STUDIO_HOST)
  --port NUMBER    port number (default 8000, or PROMPT_STUDIO_PORT)
  --python PATH    interpreter to build the virtual environment with
  --reload         restart the server when a source file changes
  --open           open the app in the default browser once it is up
  --tests          install dependencies and run the test suite, then exit
  --prepare-only   create .venv/install dependencies, then exit
  -h, --help       show this help

The server reads the API key from PROMPT_STUDIO_API_KEY / GEMINI_API_KEY when the
variable is set, otherwise from config.json (or the Settings screen in the browser).
HELP
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --host) [ "$#" -ge 2 ] || fail "--host needs a value"; HOST="$2"; shift 2 ;;
        --port) [ "$#" -ge 2 ] || fail "--port needs a value"; PORT="$2"; shift 2 ;;
        --python) [ "$#" -ge 2 ] || fail "--python needs a value"; PYTHON_BIN="$2"; shift 2 ;;
        --reload) RELOAD=1; shift ;;
        --open) OPEN_BROWSER=1; shift ;;
        --tests) RUN_TESTS=1; shift ;;
        --prepare-only) PREPARE_ONLY=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) fail "Unknown option: $1  (run ./run.sh --help)" ;;
    esac
done

case "$PORT" in
    ''|*[!0-9]*) fail "--port must be a number, got: $PORT" ;;
esac
[ "$PORT" -ge 1 ] && [ "$PORT" -le 65535 ] || fail "--port must be between 1 and 65535"

case "$HOST" in
    *[!A-Za-z0-9._:-]*) fail "--host contains unsupported characters: $HOST" ;;
esac

[ -f "$REQ_FILE" ] || fail "$REQ_FILE is missing - clone the whole repository, or run this script from inside it."

python_is_new_enough() {
    "$1" -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3, ${MIN_PYTHON_MINOR}) else 1)" >/dev/null 2>&1
}

find_python() {
    local candidate
    for candidate in python3 python /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
        if command -v "$candidate" >/dev/null 2>&1 && python_is_new_enough "$candidate"; then
            command -v "$candidate"
            return
        fi
    done
    local versioned
    for versioned in /opt/homebrew/bin/python3.13 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3.11 \
                     /usr/local/bin/python3.13 /usr/local/bin/python3.12 /usr/local/bin/python3.11 \
                     /usr/bin/python3.13 /usr/bin/python3.12 /usr/bin/python3.11; do
        if [ -x "$versioned" ] && python_is_new_enough "$versioned"; then
            printf '%s' "$versioned"
            return
        fi
    done
    return 1
}

step "Checking for Python 3.${MIN_PYTHON_MINOR} or newer"
if [ -n "$PYTHON_BIN" ]; then
    # Validated outside the subshell below so the message is the only thing printed
    # and the exit code is this shell's, not a fork's.
    python_is_new_enough "$PYTHON_BIN" || fail "'$PYTHON_BIN' is not a usable Python 3.${MIN_PYTHON_MINOR}+ interpreter."
    PY="$PYTHON_BIN"
elif ! PY="$(find_python)"; then
    say "No usable Python interpreter was found. Install one, then run ./run.sh again:" >&2
    case "$(uname -s)" in
        Darwin) say "  brew install python3          (Homebrew: https://brew.sh)" >&2 ;;
        Linux)  say "  sudo apt update && sudo apt install -y python3 python3-venv   # Debian/Ubuntu" >&2
                say "  sudo dnf install python3                                    # Fedora" >&2 ;;
        *)      say "  https://www.python.org/downloads/" >&2 ;;
    esac
    fail "Python 3.${MIN_PYTHON_MINOR}+ is required."
fi
say "    using: $PY ($("$PY" -c 'import platform; print(platform.python_version())'))"

step "Preparing the virtual environment in $VENV_DIR/"
if [ -d "$VENV_DIR" ] && [ ! -x "$VENV_PY" ]; then
    fail "$VENV_DIR exists but has no working interpreter inside it. Move the folder aside (mv $VENV_DIR ${VENV_DIR}.broken) and run ./run.sh again, or point it at an interpreter with --python /path/to/python3."
fi
if [ ! -x "$VENV_PY" ]; then
    if ! "$PY" -m venv "$VENV_DIR"; then
        fail "Could not create the virtual environment. On Debian/Ubuntu the venv module is a separate package: sudo apt install -y python3-venv"
    fi
fi

step "Installing pinned dependencies"
CURRENT_HASH="$(PS_REQ="$REQ_FILE" "$VENV_PY" - <<'HASH'
import hashlib
import os
import pathlib

print(hashlib.sha256(pathlib.Path(os.environ["PS_REQ"]).read_bytes()).hexdigest())
HASH
)"
PREVIOUS_HASH=""
[ -f "$HASH_FILE" ] && PREVIOUS_HASH="$(cat "$HASH_FILE")"
if [ "$CURRENT_HASH" != "$PREVIOUS_HASH" ]; then
    "$VENV_PY" -m pip install --upgrade pip --quiet --disable-pip-version-check \
        || fail "pip could not be upgraded. Check your network connection, then run ./run.sh again."
    "$VENV_PY" -m pip install -r "$REQ_FILE" --disable-pip-version-check \
        || fail "Dependency installation failed. This step needs internet access the first time you run the script."
    printf '%s\n' "$CURRENT_HASH" > "$HASH_FILE"
else
    say "    already satisfied (requirements.txt unchanged)"
fi

if [ "$PREPARE_ONLY" = 1 ]; then
    step "Setup complete"
    say "    Environment ready at $SCRIPT_DIR/$VENV_DIR"
    exit 0
fi

if [ "$RUN_TESTS" = 1 ]; then
    step "Running the test suite"
    exec "$VENV_PY" -m unittest discover -s tests -v
fi

step "Checking that port $PORT is free on $HOST"
if ! PS_HOST="$HOST" PS_PORT="$PORT" "$VENV_PY" - <<'PYCHECK'
import os
import socket
import sys

host = os.environ["PS_HOST"]
port = int(os.environ["PS_PORT"])
probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    probe.bind((host, port))
except OSError:
    sys.exit(1)
finally:
    probe.close()
PYCHECK
then
    say "Something is already listening on $HOST:$PORT - usually an older instance of this app." >&2
    say "Stop it, or choose another port:  ./run.sh --port 8005" >&2
    fail "Port $PORT is busy."
fi

case "$HOST" in
    127.0.0.1 | localhost) ;;
    *) say ""
       say "  \033[1;33mWARNING\033[0m binding to $HOST lets other machines on this network use"
       say "  your Gemini API key through this page. Only do that on a network you trust." ;;
esac

if [ -z "${PROMPT_STUDIO_API_KEY:-}${GEMINI_API_KEY:-}" ] && [ ! -f config.json ]; then
    say ""
    say "  No API key configured yet: open the page, press «تنظیمات / Settings» and paste"
    say "  a Google AI Studio key (https://aistudio.google.com/apikey). It is stored in"
    say "  config.json with owner-only permissions and never sent back to the browser."
fi

URL="http://$HOST:$PORT"
CMD=("$VENV_PY" -m uvicorn "prompt_compiler.app:app" --host "$HOST" --port "$PORT" --no-access-log)
[ "$RELOAD" = 1 ] && CMD+=(--reload)

step "Starting MAPSIM Prompt Studio"
say "    $URL   (press Ctrl+C to stop)"
if [ "$OPEN_BROWSER" = 1 ]; then
    { sleep 1; case "$(uname -s)" in Darwin) open "$URL" ;; *) xdg-open "$URL" >/dev/null 2>&1 ;; esac; } &
fi

exec "${CMD[@]}"
