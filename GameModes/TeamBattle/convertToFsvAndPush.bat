@echo off
cd /d "%~dp0"

python fsv2csv.py to_fsv CharaStatus.csv
git pull
git add .
git commit -m "Team CharaStatus change"
git push
pause

