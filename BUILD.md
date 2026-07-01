# Building & releasing the launcher

The launcher ships as a **single self-contained executable per OS**, built with
[PyInstaller](https://pyinstaller.org/). It bundles Python, Tkinter and pygame,
so players install nothing.

## Pieces

| File | Role |
|------|------|
| `bootstrap.py` | Frozen entry point. Updates the patch, then runs it with the bundled runtime. |
| `updater.py` | Stdlib-only updater (full download on first run, file-level deltas after). Used by the bootstrap **and** the in-app Refresh/Launch buttons. No Git. |
| `Bleach Rebirth of Souls Community Patch.py` | The actual launcher GUI (downloaded as part of the patch, so its code updates without rebuilding the .exe). |
| `bleach_launcher.spec` | PyInstaller recipe. Bundles pygame, `updater.py`, and the window icon. |
| `.github/workflows/build.yml` | CI that builds Windows + Linux binaries and attaches them to a Release. |

## Why this keeps "auto-update every launch"

The executable is just a thin bootstrap carrying the runtime. The real launcher
code is downloaded as part of the patch payload, so shipping a code change is
the same as before: push to `main`, and players get it on their next launch.
You only need to rebuild/redistribute the **.exe** when you add a *new bundled
library* (e.g. a new `import` of a third-party package) - rare.

## Releasing (recommended: CI)

1. Commit your changes to `main`.
2. Tag a version and push it:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. GitHub Actions builds `BleachCommunityPatch-windows.exe` and
   `BleachCommunityPatch-linux` and attaches them to the `v1.0.0` Release.

You can also trigger a build manually from the **Actions** tab
("Build launcher" -> "Run workflow"); binaries appear as downloadable
artifacts.

## Building locally

PyInstaller does **not** cross-compile - build on the OS you are targeting.

```bash
pip install pyinstaller pygame
# Linux also needs Tkinter: sudo apt-get install -y python3-tk
pyinstaller --noconfirm bleach_launcher.spec
# result: dist/BleachCommunityPatch(.exe)
```

## Running from source (no build)

```bash
python3 bootstrap.py
```
Run inside a full checkout, it updates that checkout in place. (Requires
Python with Tkinter + pygame; the frozen build is what removes those deps for
players.)

## Adding macOS later

Add a `macos-latest` entry to the matrix in `build.yml` (asset name e.g.
`BleachCommunityPatch-macos`). Unsigned apps need a one-time right-click ->
Open; notarization (Apple Developer account) removes that.
