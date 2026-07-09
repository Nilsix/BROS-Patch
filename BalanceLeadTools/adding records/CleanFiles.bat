@echo off
cd /d "%~dp0"
del /Q "sourceFile\*.*"
del /Q "moddedFile\*.*"
echo Cleaned sourceFile and moddedFile.
pause
