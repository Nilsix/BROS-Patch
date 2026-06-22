@echo off

python fsv2csv.py to_fsv CharaStatus.csv
pause
cd ..
cd ..
git pull
git add .
git commit -m "Team CharaStatus change"
git push

