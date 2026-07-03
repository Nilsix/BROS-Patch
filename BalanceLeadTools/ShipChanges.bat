@echo off
cd ..
git pull
set /p commitText=Name of the commit : 
git add .
git commit -m "%commitText%"
git push

pause

cd ..
py Bleach Rebirth of Souls Community Patch.py