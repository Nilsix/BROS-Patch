#!/usr/bin/env bash
#
# Bleach: Rebirth of Souls - Community Patch
# One-shot Linux installer. Run this file once and it sets everything up.
#
#   chmod +x InstallerLinux.sh && ./InstallerLinux.sh
#
# Works on Debian/Ubuntu (apt), Fedora/RHEL (dnf), Arch (pacman) and
# openSUSE (zypper). Installs Python 3 + Tkinter + pygame + Git, then
# clones (or updates) the patch. Safe to run more than once.

set -euo pipefail

REPO_URL="https://github.com/Nilsix/Bleach-Rebirth-of-Souls-Community-Patch.git"
REPO_DIR="Bleach-Rebirth-of-Souls-Community-Patch"
LAUNCHER="Bleach Rebirth of Souls Community Patch.py"

say()  { printf '\n\033[1;36m==>\033[0m %s\n' "$1"; }
ok()   { printf '\033[1;32m   ok\033[0m %s\n' "$1"; }
die()  { printf '\n\033[1;31mError:\033[0m %s\n' "$1" >&2; exit 1; }

# --- privilege helper: use sudo only if we are not already root -------------
if [ "$(id -u)" -eq 0 ]; then
  SUDO=""
else
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  else
    die "This script needs root to install packages, but 'sudo' was not found. Re-run as root."
  fi
fi

# --- detect the package manager ---------------------------------------------
say "Detecting your Linux package manager..."
if   command -v apt-get >/dev/null 2>&1; then PM="apt"
elif command -v dnf      >/dev/null 2>&1; then PM="dnf"
elif command -v pacman   >/dev/null 2>&1; then PM="pacman"
elif command -v zypper   >/dev/null 2>&1; then PM="zypper"
else
  die "Could not find a supported package manager (apt, dnf, pacman, zypper).
Please install manually: python3, python3-tk/tkinter, python3-pip, git, and python3-pygame."
fi
ok "Using $PM"

# --- install system dependencies --------------------------------------------
# Note: python3-tk is REQUIRED - the launcher uses Tkinter for its window.
# We install pygame from the distro repo when possible (avoids PEP 668 issues).
say "Installing Python 3, Tkinter, pip, Git and pygame (you may be asked for your password)..."
case "$PM" in
  apt)
    $SUDO apt-get update
    $SUDO apt-get install -y python3 python3-tk python3-pip git python3-pygame
    ;;
  dnf)
    $SUDO dnf install -y python3 python3-tkinter python3-pip git python3-pygame
    ;;
  pacman)
    $SUDO pacman -Sy --needed --noconfirm python tk python-pip git python-pygame
    ;;
  zypper)
    $SUDO zypper --non-interactive install python3 python3-tk python3-pip git python3-pygame
    ;;
esac
ok "System packages installed"

# --- find a Python that has Tkinter -----------------------------------------
PY=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "import tkinter" >/dev/null 2>&1; then
    PY="$cand"; break
  fi
done
[ -n "$PY" ] || die "Python 3 with Tkinter is still not available. Check that the install step above succeeded."
ok "Python: $($PY --version 2>&1) at $(command -v "$PY")"

# --- make sure pygame is importable (fallback to pip if distro pkg missing) --
if ! "$PY" -c "import pygame" >/dev/null 2>&1; then
  say "Installing pygame via pip as a fallback..."
  "$PY" -m pip install --user --upgrade pygame \
    || "$PY" -m pip install --user --break-system-packages --upgrade pygame \
    || die "Could not install pygame. Try: $PY -m pip install --user pygame"
fi
ok "pygame is available"

# --- clone or update the patch ----------------------------------------------
if [ -d "$REPO_DIR/.git" ]; then
  say "Patch already downloaded - updating it..."
  git -C "$REPO_DIR" pull --ff-only || die "Update failed. Delete the '$REPO_DIR' folder and run this again."
  ok "Patch updated"
else
  say "Downloading the patch..."
  git clone "$REPO_URL" "$REPO_DIR" || die "Download failed. Check your internet connection and try again."
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
