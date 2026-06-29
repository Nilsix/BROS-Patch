@echo off
if exist CharaStatus.csv (
	python fsv2csv.py to_fsv CharaStatus.csv
)

if exist CommonParam.csv (
	python fsv2csv.py to_fsv "CommonParam.csv
)


