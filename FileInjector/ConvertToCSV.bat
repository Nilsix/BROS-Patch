@echo off

python fsv2csv.py to_csv "..\Files\Bleach Rebirth of Souls Community Patch\Script\CharaStatus.fsv"
python fsv2csv.py to_csv "..\Files\Bleach Rebirth of Souls Community Patch\Script\CommonParam.fsv"
move "..\Files\Bleach Rebirth of Souls Community Patch\Script\Charastatus.csv"
move "..\Files\Bleach Rebirth of Souls Community Patch\Script\CommonParam.csv"
