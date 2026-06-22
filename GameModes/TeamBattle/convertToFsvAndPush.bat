@echo off
if exist CharaStatus.fsv (
	python fsv2csv.py to_csv CharaStatus.fsv
)

cd ..
cd ..
git pull
git add .
git commit -m "Team CharaStatus change"
git push


pause