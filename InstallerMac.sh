#!/bin/bash
#
# Bleach: Rebirth of Souls - Community Patch
# One-shot macOS installer. Run this file once and it sets everything up.
#
#   chmod +x InstallerMac.sh && ./InstallerMac.sh
#
# Installs (via Homebrew) Python 3 + Tkinter + Git, then clones or updates the
# patch. Safe to run more than once.

set -euo pipefail

REPO_URL="https://github.com/Nilsix/Bleach-Rebirth-of-Souls-Community-Patch.git"
REPO_DIR="Bleach-Rebirth-of-Souls-Community-Patch"
LAUNCHER="Bleach Rebirth of Souls Community Patch.py"

say()  { printf '\n\033[1;36m==>\033[0m %s\n' "$1"; }
ok()   { printf '\033[1;32m   ok\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m   warning\033[0m %s\n' "$1"; }
die()  { printf '\n\033[1;31mError:\033[0m %s\n' "$1" >&2; exit 1; }

# --- make sure Homebrew is installed and on PATH ----------------------------
# On Apple Silicon brew lives in /opt/homebrew; on Intel in /usr/local.
if ! command -v brew >/dev/null 2>&1; then
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    [ -x "$b" ] && eval "$("$b" shellenv)" && break
  done
fi
if ! command -v brew >/dev/null 2>&1; then
  die "Homebrew is required but was not found.
Install it by pasting this line into Terminal, then run this installer again:

  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
fi
ok "Homebrew found: $(command -v brew)"

# --- install Python 3, Tkinter and Git --------------------------------------
# IMPORTANT: Homebrew's Python does NOT bundle Tkinter - it comes from the
# separate 'python-tk' formula, which the launcher's window needs.
say "Installing Python 3, Tkinter and Git via Homebrew..."
brew install python git python-tk || die "Homebrew failed to install the dependencies. Run 'brew doctor' and try again."
ok "Dependencies installed"

# --- find a Python that has Tkinter -----------------------------------------
PY=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "import tkinter" >/dev/null 2>&1; then
    PY="$cand"; break
  fi
done
[ -n "$PY" ] || die "Python 3 with Tkinter is still not available. Try 'brew reinstall python python-tk'."
ok "Python: $($PY --version 2>&1) at $(command -v "$PY")"

# --- make sure requests is importable (non-fatal) ---------------------------
if ! "$PY" -c "import requests" >/dev/null 2>&1; then
  say "Installing requests via pip..."
  if "$PY" -m pip install --user --upgrade requests >/dev/null 2>&1 \
     || "$PY" -m pip install --user --break-system-packages --upgrade requests >/dev/null 2>&1; then
    ok "requests installed"
  else
    warn "Could not install 'requests'. The launcher will still work; only the online version check is skipped."
  fi
else
  ok "requests is available"
fi

# --- clone or update the patch ----------------------------------------------
if [ -d "$REPO_DIR/.git" ]; then
  say "Patch already downloaded - updating it..."
  git -C "$REPO_DIR" config core.longpaths true || true
  git -C "$REPO_DIR" pull --ff-only || die "Update failed. Delete the '$REPO_DIR' folder and run this again."
  ok "Patch updated"
else
  say "Downloading the patch..."
  git clone -c core.longpaths=true "$REPO_URL" "$REPO_DIR" || die "Download failed. Check your internet connection and try again."
  ok "Patch downloaded"
fi

# --- make the launcher runnable ---------------------------------------------
LAUNCHER_PATH="$REPO_DIR/$LAUNCHER"
[ -f "$LAUNCHER_PATH" ] && chmod +x "$LAUNCHER_PATH" 2>/dev/null || true

# --- done -------------------------------------------------------------------
say "Installation complete!"
cat <<EOF

To start the Community Patch Launcher, run:

    $PY "$LAUNCHER_PATH"

EOF
