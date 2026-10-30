
#!/usr/bin/env bash
# Remove the MAPSIM Prompt Studio systemd service.
# Project files, .venv, configuration, library and usage data are preserved.

set -Eeuo pipefail

SERVICE_NAME="mapsim-prompt-studio"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# --------------------------------------------------
# Platform and permission checks
# --------------------------------------------------

if [[ "$(uname -s)" != Linux ]]; then
    echo "This script requires Linux." >&2
    exit 1
fi

if [[ "${EUID}" -ne 0 ]]; then
    echo "Run this script as root." >&2
    exit 1
fi

if ! command -v systemctl >/dev/null 2>&1 ||
   ! systemctl --version >/dev/null 2>&1; then
    echo "systemd was not detected." >&2
    exit 1
fi

# --------------------------------------------------
# Check service installation
# --------------------------------------------------

if [[ ! -f "$SERVICE_FILE" ]]; then
    echo "MAPSIM Prompt Studio service is not installed."
    exit 0
fi

# --------------------------------------------------
# Stop and remove service
# --------------------------------------------------

echo "Stopping MAPSIM Prompt Studio..."

systemctl disable --now "$SERVICE_NAME" 2>/dev/null || true

echo "Removing systemd service unit..."

rm -f "$SERVICE_FILE"

systemctl daemon-reload
systemctl reset-failed "$SERVICE_NAME" 2>/dev/null || true

# --------------------------------------------------
# Final report
# --------------------------------------------------

echo
echo "MAPSIM Prompt Studio service removed successfully."
echo
echo "The following have been preserved:"
echo "  - Project source files"
echo "  - Python virtual environment (.venv)"
echo "  - config.json"
echo "  - library.json"
echo "  - usage.json"
echo
echo "No project files or application data were deleted."
