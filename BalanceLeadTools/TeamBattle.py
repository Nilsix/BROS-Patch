import csv
import os     
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEAM_BATTLE_DIR = os.path.join(BASE_DIR,"..","GameModes","TeamBattle")
gameVersionsPath = os.path.join(BASE_DIR,"..","GameVersions")

gameVersionsList = []
for folder in os.listdir(gameVersionsPath):
    gameVersionsList.append(folder)


def checkTokenOpen():
    if os.path.exists(os.path.join(TEAM_BATTLE_DIR,"TokenOpen.txt")):
        return True
    return False


def applyKonpakuChanges(id,value):
    revValue = value
    if id == "35" and value == 9:
        value = 5
    elif id == "01" or id == "20":
        if value == 9:
            value = 8
        revValue +=2

    id = "pl0"+id
    csvPath = os.path.join(TEAM_BATTLE_DIR,"CharaStatus.csv")
    with open(csvPath,"r",encoding="utf8") as f:
        rows = list(csv.DictReader(f))
        for row in rows:
            if row["_csv0"] == id:
                row["soul_num"] = value
                row["evo_soul_num"] = value
                row["rev_soul_num"] = revValue

    with open(csvPath,"w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

options = -1
if checkTokenOpen() == False:
    options = int(input("""Quit (0)
Open server (1)

Choose an option : """))

    if options == 1:
        for i,version in enumerate(gameVersionsList):
            print(f"{i} = {version}")
        chooseGameVersion = int(input("Choose a game version : "))
        
        
        open(os.path.join(TEAM_BATTLE_DIR,"TokenOpen.txt"), "w").close()
        shutil.copy(os.path.join(gameVersionsPath,gameVersionsList[chooseGameVersion],"Script","CharaStatus.fsv"),os.path.join(TEAM_BATTLE_DIR,"CharaStatus.fsv"))
        subprocess.run("convertToCsv.bat",shell=True,cwd=TEAM_BATTLE_DIR)
    exit()

options = int(input("""
Quit (0)               
Update CharaStatus (1)
Reset CharaStatus (2)
Close server (3)

Choose an option : """))
    
if options == 0:
    exit()
elif options == 1:
    print("""00 = ICHIGO KUROSAKI
01 = ICHIGO KUROSAKI (BANKAI)
02 = ICHIGO KUROSAKI (FINAL GETSUGATENSHO)
03 = URYU ISHIDA
04 = YASUTORA SADO
06 = KISUKE URAHARA
07 = YORUICHI SHIHOIN
08 = RENJI ABARAI
10 = RUKIA KUCHIKI
11 = SHUHEI HISAGI
12 = RANGIKU MATSUMOTO
13 = IZURU KIRA
14 = IKKAKU MADARAME
15 = YUMICHIKA AYASEGAWA
16 = SHIGEKUNI GENRYUSAI YAMAMOTO
17 = SOI FON
18 = GIN ICHIMARU
19 = RETSU UNOHANA
20 = SOSUKE AIZEN
22 = BYAKUYA KUCHIKI
23 = SAJIN KOMAMURA
24 = SHUNSUI KYORAKU
25 = KANAME TOSEN
26 = TOSHIRO HITSUGAYA
27 = KENPACHI ZARAKI
29 = MAYURI KUROTSUCHI 
31 = KAIEN SHIBA
32 = SHINJI HIRAKO
33 = COYOTE STARK
35 = TIER HALIBEL
36 = ULQUIORRA SHIFAR
37 = NNOITORA GILGA
38 = GRIMMJOW JEAGERJAQUES
39 = SZAYELAPORRO GRANTZ
42 = NELLIEL TU ODELSCHWANCK
50 = ICHIBE HOUSUBE 
51 = ICHIGO KUROSAKI TYBW
52 = YHWACH""")

    WinnerInput = input("\nWinner ID : ")
    winnerKonpakuRemaining = int(input("remaining konpakus : "))
    LoserInput = input("\nLoser ID : ")

    applyKonpakuChanges(WinnerInput, winnerKonpakuRemaining)
    applyKonpakuChanges(LoserInput, 9)
    subprocess.run([os.path.join(TEAM_BATTLE_DIR,"convertToFsvAndPush.bat")], shell=True)
    print("\nChanges applied")
elif options == 2:
    subprocess.run([os.path.join(TEAM_BATTLE_DIR,"resetCharaStatus.bat")], shell=True)
elif options == 3:
    os.remove(os.path.join(TEAM_BATTLE_DIR,"TokenOpen.txt"))
    os.remove(os.path.join(TEAM_BATTLE_DIR,"CharaStatus.csv"))
    os.remove(os.path.join(TEAM_BATTLE_DIR,"CharaStatus.fsv"))
