
#!/usr/bin/env bash
# Install MAPSIM Prompt Studio as a systemd service on Linux.
# The installer and application service run as root.
# Supports localhost (127.0.0.1) and all network interfaces (0.0.0.0).

set -Eeuo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
SERVICE_NAME="mapsim-prompt-studio"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

HOST="${PROMPT_STUDIO_HOST:-127.0.0.1}"
PORT="${PROMPT_STUDIO_PORT:-8000}"

# --------------------------------------------------
# Platform and permission checks
# --------------------------------------------------

if [[ "$(uname -s)" != Linux ]]; then
    echo "This installer requires Linux with systemd." >&2
    exit 1
fi

if [[ "${EUID}" -ne 0 ]]; then
    echo "Run this installer as root." >&2
    exit 1
fi

if ! command -v systemctl >/dev/null 2>&1 ||
   ! systemctl --version >/dev/null 2>&1; then
    echo "systemd was not detected." >&2
    exit 1
fi

# --------------------------------------------------
# Project validation
# --------------------------------------------------

if [[ ! -f "$SCRIPT_DIR/requirements.txt" ||
      ! -f "$SCRIPT_DIR/run.sh" ]]; then
    echo "Run this script from the MAPSIM Prompt Studio project directory." >&2
    exit 1
fi

if [[ ! -f "$SCRIPT_DIR/prompt_compiler/app.py" ]]; then
    echo "Application entry point was not found." >&2
    exit 1
fi

# --------------------------------------------------
# Host and port validation
# --------------------------------------------------

case "$HOST" in
    127.0.0.1|0.0.0.0)
        ;;
    *)
        echo "Invalid PROMPT_STUDIO_HOST." >&2
        echo "Supported values: 127.0.0.1 or 0.0.0.0" >&2
        exit 1
        ;;
esac

if [[ ! "$PORT" =~ ^[0-9]+$ ]] ||
   (( PORT < 1 || PORT > 65535 )); then
    echo "PROMPT_STUDIO_PORT must be between 1 and 65535." >&2
    exit 1
fi

# --------------------------------------------------
# Existing service check
# --------------------------------------------------

if [[ -f "$SERVICE_FILE" ]]; then
    echo "Service already exists: $SERVICE_FILE" >&2
    echo "Remove it first with ./uninstall_service.sh" >&2
    exit 1
fi

# --------------------------------------------------
# Port availability check
# --------------------------------------------------

if command -v ss >/dev/null 2>&1; then
    if ss -H -lnt 2>/dev/null |
       awk -v port=":$PORT" '$4 ~ (port "$") { found=1 } END { exit !found }'; then
        echo "Port $PORT is already in use." >&2
        exit 1
    fi
else
    echo "Warning: ss command not found; port availability was not checked." >&2
fi

# --------------------------------------------------
# Python environment preparation
# --------------------------------------------------

echo "Preparing MAPSIM Prompt Studio environment..."

bash "$SCRIPT_DIR/run.sh" --prepare-only

if [[ ! -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
    echo "Python virtual environment was not created successfully." >&2
    exit 1
fi

"$SCRIPT_DIR/.venv/bin/python" -c \
    "from prompt_compiler.app import app; print('Application import: OK')" \
    || {
        echo "Application import failed." >&2
        exit 1
    }

# --------------------------------------------------
# Generate systemd service
# --------------------------------------------------

TMP_UNIT="$(mktemp)"
trap 'rm -f "$TMP_UNIT"' EXIT

cat > "$TMP_UNIT" <<UNIT
[Unit]
Description=MAPSIM Prompt Studio
After=network.target

[Service]
Type=simple

User=root
Group=root

WorkingDirectory=$SCRIPT_DIR

Environment=PYTHONUNBUFFERED=1
Environment=PYTHONDONTWRITEBYTECODE=1
Environment=PROMPT_STUDIO_HOST=$HOST
Environment=PROMPT_STUDIO_PORT=$PORT

UMask=0077

ExecStart=$SCRIPT_DIR/.venv/bin/python -m uvicorn prompt_compiler.app:app --host $HOST --port $PORT --no-access-log

Restart=on-failure
RestartSec=3

StandardOutput=journal
StandardError=journal

LogLevelMax=warning
LogRateLimitIntervalSec=30s
LogRateLimitBurst=100

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$SCRIPT_DIR

[Install]
WantedBy=multi-user.target
UNIT

# --------------------------------------------------
# Install and start service
# --------------------------------------------------

install -o root -g root -m 0644 "$TMP_UNIT" "$SERVICE_FILE"

systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"

# --------------------------------------------------
# Installation summary
# --------------------------------------------------

echo
echo "MAPSIM Prompt Studio installed successfully."
echo
echo "Service:   $SERVICE_NAME"
echo "User:      root"
echo "Host:      $HOST"
echo "Port:      $PORT"
echo

if [[ "$HOST" == "127.0.0.1" ]]; then
    echo "Access:    Localhost only"
    echo "Local URL: http://127.0.0.1:$PORT"
else
    echo "Access:    All network interfaces"
    echo "Local URL: http://127.0.0.1:$PORT"
    echo "Remote URL: http://SERVER_PUBLIC_IP:$PORT"
    echo
    echo "IMPORTANT: Check firewall rules before external access."
    echo "Use HTTPS and authentication before exposing the application publicly."
fi

echo
echo "Status:    systemctl status $SERVICE_NAME"
echo "Logs:      journalctl -u $SERVICE_NAME -f"
echo "Stop:      systemctl stop $SERVICE_NAME"
echo "Restart:   systemctl restart $SERVICE_NAME"
echo "Remove:    ./uninstall_service.sh"
echo
echo "The service is enabled to start automatically at boot."
echo "Configure your Google AI Studio API key in application Settings."
