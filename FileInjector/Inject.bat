@echo off

python fsv2csv.py to_fsv CharaStatus.csv
python fsv2csv.py to_fsv CommonParam.csv

move "CharaStatus.fsv" "..\Files\Bleach Rebirth of Souls Community Patch\Script\"
move "CommonParam.fsv" "..\Files\Bleach Rebirth of Souls Community Patch\Script\"



ConvertToCSV

