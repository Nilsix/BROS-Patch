@echo off

python fsv2csv.py to_csv "..\GameVersions\Bleach Rebirth of Souls Community Patch\Script\CharaStatus.fsv"
python fsv2csv.py to_csv "..\GameVersions\Bleach Rebirth of Souls Community Patch\Script\CommonParam.fsv"
move "..\GameVersions\Bleach Rebirth of Souls Community Patch\Script\Charastatus.csv"
move "..\GameVersions\Bleach Rebirth of Souls Community Patch\Script\CommonParam.csv"
