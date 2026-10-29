#!/usr/bin/env bash
# Remove the systemd service unit. Project files, .venv, config, library and usage data are kept.
set -euo pipefail
SERVICE_NAME="mapsim-prompt-studio"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
if [[ "$(uname -s)" != Linux ]] || ! command -v systemctl >/dev/null 2>&1; then
  echo "This script requires Linux with systemd." >&2
  exit 1
fi
if [[ "${EUID}" -eq 0 ]]; then
  echo "Run as the normal project owner, without sudo." >&2
  exit 1
fi
sudo systemctl disable --now "$SERVICE_NAME" 2>/dev/null || true
sudo rm -f "$SERVICE_FILE"
sudo systemctl daemon-reload
sudo systemctl reset-failed "$SERVICE_NAME" 2>/dev/null || true
echo "Service removed. Project files and local data were not deleted."
