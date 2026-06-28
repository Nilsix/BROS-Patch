@echo off
cd /d "%~dp0"

copy "originalCharaStatus\CharaStatus.csv" .
call convertToFsvAndPush.bat

