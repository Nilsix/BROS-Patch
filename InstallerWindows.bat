@echo off
setlocal EnableExtensions
title Bleach: Rebirth of Souls - Community Patch Installer

echo(
echo ================================================================
echo   Bleach: Rebirth of Souls - Community Patch - Windows Installer
echo ================================================================
echo(

set "REPO_DIR=Bleach-Rebirth-of-Souls-Community-Patch"
set "REPO_URL=https://github.com/Nilsix/Bleach-Rebirth-of-Souls-Community-Patch.git"
set "LAUNCHER=Bleach Rebirth of Souls Community Patch.py"

REM ---------------------------------------------------------------------------
REM  0) Make sure winget exists (it ships with "App Installer").
REM ---------------------------------------------------------------------------
where winget >nul 2>&1
if errorlevel 1 (
    echo [ERROR] "winget" was not found on this PC.
    echo         winget comes with the "App Installer" package. Update Windows,
    echo         or install "App Installer" from the Microsoft Store, then run
    echo         this installer again.
    echo(
    pause
    exit /b 1
)

REM ---------------------------------------------------------------------------
REM  1) Install Python 3 (includes Tkinter + pip) and Git.
REM     winget returns non-zero when something is already installed, so we do
REM     NOT gate on its exit code - we verify the tools ourselves further down.
REM ---------------------------------------------------------------------------
REM  winget has no "latest" meta-id for Python - each minor version is its own
REM  package (Python.Python.3.14, 3.15, ...). Probe from newest downward and
REM  install the first line that exists in the catalog, so this stays current
REM  for years without editing the file.
echo Finding the newest available Python 3 ... (press Enter)
set "PYPKG="
for /l %%v in (25,-1,13) do (
    if not defined PYPKG (
        winget show --id Python.Python.3.%%v -e --source winget >nul 2>&1 && set "PYPKG=Python.Python.3.%%v"
    )
)
if not defined PYPKG set "PYPKG=Python.Python.3.14"
echo Installing %PYPKG% (this can take a minute) ...
winget install --id %PYPKG% -e --source winget --accept-source-agreements --accept-package-agreements --silent

echo Installing Git ...
winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements --silent

REM ---------------------------------------------------------------------------
REM  2) A freshly-installed tool is not on THIS window's PATH yet (Windows only
REM     updates PATH for new windows). Add Git's known install locations so we
REM     can use it right now, without asking the user to reopen anything.
REM ---------------------------------------------------------------------------
where git >nul 2>&1
if errorlevel 1 if exist "%ProgramFiles%\Git\cmd\git.exe"        set "PATH=%PATH%;%ProgramFiles%\Git\cmd"
where git >nul 2>&1
if errorlevel 1 if exist "%ProgramFiles(x86)%\Git\cmd\git.exe"   set "PATH=%PATH%;%ProgramFiles(x86)%\Git\cmd"
where git >nul 2>&1
if errorlevel 1 if exist "%LocalAppData%\Programs\Git\cmd\git.exe" set "PATH=%PATH%;%LocalAppData%\Programs\Git\cmd"

where git >nul 2>&1
if errorlevel 1 (
    echo(
    echo [ACTION NEEDED] Git was installed, but this window can't see it yet.
    echo                 Please CLOSE this window and double-click the installer
    echo                 one more time - it will finish the setup.
    echo(
    pause
    exit /b 1
)

REM ---------------------------------------------------------------------------
REM  3) Pick a Python command. The "py" launcher is registered globally by the
REM     Python installer, so it is usually usable in this same window.
REM ---------------------------------------------------------------------------
set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY ( where python >nul 2>&1 && set "PY=python" )
if not defined PY for /d %%d in ("%LocalAppData%\Programs\Python\Python3*") do if exist "%%d\python.exe" set "PY=%%d\python.exe"

REM ---------------------------------------------------------------------------
REM  4) Download (or update) the patch WITH long-path support.
REM
REM     core.longpaths lets git create the deep Effect\spfx\pl022\... files whose
REM     paths exceed Windows' legacy 260-character limit. Without it you get
REM     "error: unable to create file ...: Filename too long" and an incomplete
REM     download. Passing it with -c also stores it in the new repo's config, so
REM     later updates keep working. This needs NO admin rights.
REM ---------------------------------------------------------------------------
if exist "%REPO_DIR%\.git" (
    echo Patch already downloaded - updating it ...
    git -C "%REPO_DIR%" config core.longpaths true
    git -C "%REPO_DIR%" pull
) else (
    echo Downloading the patch ...
    git clone -c core.longpaths=true "%REPO_URL%" "%REPO_DIR%"
)
if errorlevel 1 (
    echo(
    echo [ERROR] The download/update failed. Check your internet connection,
    echo         delete the "%REPO_DIR%" folder if it exists, then run this again.
    echo(
    pause
    exit /b 1
)

REM ---------------------------------------------------------------------------
REM  5) Install the launcher's one third-party dependency (requests).
REM     Non-fatal: the launcher still runs without it (only a version ping uses
REM     it), so we don't abort the install if this step can't complete.
REM ---------------------------------------------------------------------------
if defined PY (
    echo Installing launcher dependencies ...
    "%PY%" -m pip install --user --upgrade requests >nul 2>&1
)

REM ---------------------------------------------------------------------------
REM  6) Launch the patch.
REM ---------------------------------------------------------------------------
echo(
echo Installation complete!
echo(
if defined PY if exist "%REPO_DIR%\%LAUNCHER%" (
    echo Starting the Community Patch launcher ...
    start "" "%PY%" "%REPO_DIR%\%LAUNCHER%"
) else (
    echo To start it, open the "%REPO_DIR%" folder and run:
    echo     %LAUNCHER%
)
echo(
pause
endlocal
