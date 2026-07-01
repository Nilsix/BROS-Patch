# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller build recipe for the Bleach Community Patch launcher.
# Produces ONE self-contained executable that bundles Python, Tkinter and
# pygame, so end users install nothing.
#
#   pip install pyinstaller pygame
#   pyinstaller --noconfirm bleach_launcher.spec
#
# Output: dist/BleachCommunityPatch(.exe on Windows)
#
# NOTE: build on the OS you want to target - PyInstaller does not
# cross-compile. CI (.github/workflows/build.yml) builds Windows + Linux.

import os
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], []

# pull in pygame fully (its compiled libs + data) so the downloaded launcher
# code can `import pygame` from inside the frozen runtime
for pkg in ("pygame",):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# bundle the updater module so the very first launch (empty payload) can update
datas += [("updater.py", ".")]

# bundle the window icon for the update splash + frozen exe icon
icon_path = os.path.join("ressources", "pimplin.ico")
if os.path.exists(icon_path):
    datas += [(icon_path, "ressources")]

a = Analysis(
    ["bootstrap.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="BleachCommunityPatch",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    # keep a console: the launcher hides it on Windows at startup and re-shows
    # it to print errors, matching the original behaviour.
    console=True,
    disable_windowed_traceback=False,
    icon=(icon_path if os.path.exists(icon_path) else None),
)
