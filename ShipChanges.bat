@echo off

git pull
set /p commitText=Name of the commit : 
git add .
git commit -m "%commitText%"
git push

pause