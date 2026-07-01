@echo off
rem Bleach Rebirth of Souls - Community Patch (Windows)
rem Downloads the latest self-contained launcher (single .exe, no Python/git
rem needed) and starts it. Just double-click this file.
setlocal
set "REPO=Nilsix/Bleach-Rebirth-of-Souls-Community-Patch"
set "ASSET=BleachCommunityPatch-windows.exe"
set "FOLDER=%LOCALAPPDATA%\BleachCommunityPatch"
set "DEST=%FOLDER%\BleachCommunityPatch.exe"
set "URL=https://github.com/%REPO%/releases/latest/download/%ASSET%"

if not exist "%FOLDER%" mkdir "%FOLDER%"
echo Downloading the latest launcher...
curl -L -o "%DEST%" "%URL%"
if errorlevel 1 (
  echo.
  echo Download failed. Please check your internet connection and try again.
  pause
  exit /b 1
)
echo Starting it now ^(first launch downloads the patch, please wait^)...
start "" "%DEST%"
endlocal
