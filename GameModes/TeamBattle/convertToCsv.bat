@echo off
if exist CharaStatus.fsv (
	python fsv2csv.py to_csv "CharaStatus.fsv"
)

if exist CommonParam.fsv (
	python fsv2csv.py to_csv "CommonParam.fsv"
)

pause


