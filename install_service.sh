#!/usr/bin/env bash
# Install MAPSIM Prompt Studio as a systemd service on Linux.
# Run as the normal project owner, not with sudo: this script requests sudo only
# for systemd operations. The app and its local data remain owned by the user.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
SERVICE_NAME="mapsim-prompt-studio"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
HOST="127.0.0.1"
PORT="${PROMPT_STUDIO_PORT:-8000}"

if [[ "$(uname -s)" != Linux ]]; then
  echo "This installer requires Linux with systemd." >&2
  exit 1
fi
if ! command -v systemctl >/dev/null 2>&1 || ! systemctl --version >/dev/null 2>&1; then
  echo "systemd was not detected. This script supports systemd-based Linux distributions." >&2
  exit 1
fi
if [[ "${EUID}" -eq 0 ]]; then
  echo "Run this script as the normal user who owns the project, without sudo." >&2
  echo "It will request sudo only when installing the service unit." >&2
  exit 1
fi
if [[ ! -f "$SCRIPT_DIR/requirements.txt" || ! -f "$SCRIPT_DIR/run.sh" ]]; then
  echo "Run this script from the MAPSIM Prompt Studio project directory." >&2
  exit 1
fi
if [[ ! "$PORT" =~ ^[0-9]+$ ]] || (( PORT < 1 || PORT > 65535 )); then
  echo "PROMPT_STUDIO_PORT must be a number between 1 and 65535." >&2
  exit 1
fi

# Build the environment as the project owner; never create root-owned venv/data.
bash "$SCRIPT_DIR/run.sh" --prepare-only

TMP_UNIT="$(mktemp)"
trap 'rm -f "$TMP_UNIT"' EXIT
cat > "$TMP_UNIT" <<UNIT
[Unit]
Description=MAPSIM Prompt Studio
After=network.target

[Service]
Type=simple
User=$(id -un)
Group=$(id -gn)
WorkingDirectory=$SCRIPT_DIR
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONDONTWRITEBYTECODE=1
Environment=PROMPT_STUDIO_HOST=$HOST
Environment=PROMPT_STUDIO_PORT=$PORT
UMask=0077
ExecStart=$SCRIPT_DIR/.venv/bin/python -m uvicorn prompt_compiler.app:app --host $HOST --port $PORT --no-access-log
Restart=on-failure
RestartSec=3
# Keep routine request logs off; systemd retains warnings/errors and rate-limits bursts.
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

sudo install -o root -g root -m 0644 "$TMP_UNIT" "$SERVICE_FILE"
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"

echo
echo "Installed and started: $SERVICE_NAME"
echo "Local URL: http://127.0.0.1:$PORT"
echo "Status:    sudo systemctl status $SERVICE_NAME"
echo "Logs:      sudo journalctl -u $SERVICE_NAME -p warning --since today"
echo "Stop:      sudo systemctl stop $SERVICE_NAME"
echo "Remove:    ./uninstall_service.sh"
echo
echo "The service starts on boot. Open the URL and add your Google AI Studio API key in Settings if you have not done so."
