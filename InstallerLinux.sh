#!/usr/bin/env bash
#
# Bleach Rebirth of Souls - Community Patch (Linux)
#
# Downloads the latest self-contained launcher (a single binary - no Python,
# git, pygame or anything else to install) and runs it. The launcher then
# downloads/updates the patch itself on every start.
#
# Usage:  chmod +x InstallerLinux.sh && ./InstallerLinux.sh
# Safe to re-run any time to grab the newest launcher build.

set -euo pipefail

REPO="Nilsix/Bleach-Rebirth-of-Souls-Community-Patch"
ASSET="BleachCommunityPatch-linux"
DEST="${HOME}/.local/bin/BleachCommunityPatch"
URL="https://github.com/${REPO}/releases/latest/download/${ASSET}"

mkdir -p "$(dirname "$DEST")"
echo "Downloading the latest launcher..."
if command -v curl >/dev/null 2>&1; then
  curl -fL --progress-bar -o "$DEST" "$URL"
elif command -v wget >/dev/null 2>&1; then
  wget -q --show-progress -O "$DEST" "$URL"
else
  echo "Error: need 'curl' or 'wget' to download. Install one and re-run." >&2
  exit 1
fi

chmod +x "$DEST"
echo "Launcher installed at: $DEST"
echo "Starting it now (first launch downloads the patch, please wait)..."
exec "$DEST"
