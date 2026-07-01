# Bleach: Rebirth of Souls - Community Patch Launcher

A one-click launcher for the community patch. **No Python, no Git, nothing to
install** - you download a single file and run it. It keeps the patch up to
date by itself every time you open it.

## Install & play

**Windows**
1. Download **`BleachCommunityPatch-windows.exe`** from the
   [latest release](https://github.com/Nilsix/Bleach-Rebirth-of-Souls-Community-Patch/releases/latest).
2. Double-click it. The first launch downloads the patch (a few hundred MB,
   one time); after that it starts quickly and only grabs what changed.

*(Optional: `InstallerWindows.bat` just downloads that same .exe for you.)*

**Linux**
1. Download **`BleachCommunityPatch-linux`** from the
   [latest release](https://github.com/Nilsix/Bleach-Rebirth-of-Souls-Community-Patch/releases/latest).
2. Make it executable and run it:
   ```bash
   chmod +x BleachCommunityPatch-linux && ./BleachCommunityPatch-linux
   ```
   Or run `InstallerLinux.sh`, which downloads and starts it for you.

*(macOS build is not available yet.)*

## How updates work

The launcher checks GitHub on every start. The first time it downloads the
whole patch; afterwards it fetches **only the files that changed** - fast, and
no Git required. Your settings (`Json/config.json`) are never touched by an
update.

The downloaded patch lives in:

- Windows: `%LOCALAPPDATA%\BleachCommunityPatch\patch`
- Linux: `~/.local/share/BleachCommunityPatch/patch`

Delete that folder if you ever want a clean re-download.

## For maintainers

See [BUILD.md](BUILD.md) for how the executables are built and released.
