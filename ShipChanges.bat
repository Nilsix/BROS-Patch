@echo off

git pull
set /p commitText=Name of the commit : 
echo %commitText%
git add .
git commit -m "%commitText%"
git push

pause