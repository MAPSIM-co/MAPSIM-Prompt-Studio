
#!/usr/bin/env bash
# Remove the MAPSIM Prompt Studio systemd service.
# Project files, .venv, configuration, library and usage data are preserved.
set -Eeuo pipefail

SERVICE_NAME="mapsim-prompt-studio"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

if [[ "$(uname -s)" != Linux ]]; then
  echo "This script requires Linux." >&2
  exit 1
fi

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script as root." >&2
  echo "Example: sudo ./uninstall_service.sh" >&2
  exit 1
fi

if ! command -v systemctl >/dev/null 2>&1 ||
   ! systemctl --version >/dev/null 2>&1; then
  echo "systemd was not detected." >&2
  exit 1
fi

echo "Stopping and disabling MAPSIM Prompt Studio..."

systemctl disable --now "$SERVICE_NAME" 2>/dev/null || true

if [[ -f "$SERVICE_FILE" ]]; then
  rm -f "$SERVICE_FILE"
fi

systemctl daemon-reload
systemctl reset-failed "$SERVICE_NAME" 2>/dev/null || true

echo
echo "MAPSIM Prompt Studio service has been removed."
echo
echo "Preserved:"
echo "  - Project source files"
echo "  - Python virtual environment (.venv)"
echo "  - config.json"
echo "  - library.json"
echo "  - usage.json"
echo
echo "No project files or application data were deleted."
