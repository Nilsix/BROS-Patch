@echo off
set /p commitText=Name of the commit : 
git pull
git add .
git commit -m "%commitText"
git push