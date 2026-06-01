import tkinter as tk
import json
from tkinter import filedialog
import shutil
import os
import subprocess


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


try:
    result = subprocess.run(["git", "-C", BASE_DIR, "pull"], check=True, capture_output=True, text=True)
    output = result.stdout.strip()
    if "Already up to date." in output:
        print("Mod is already up to date.")
    else:
        print("Mod updated successfully.")
        updated = True

except Exception as e:
    print("Git update failed :", e)

try :
    template_path = os.path.join(BASE_DIR,"configTemplate.json")
    config_path = os.path.join(BASE_DIR,"config.json")
    if not os.path.exists(config_path):
        shutil.copy(template_path,config_path)

except Exception as e: 
    print(e)
config_path = os.path.join(BASE_DIR, "config.json")

if not os.path.exists(config_path):
    with open(config_path, "w") as f:
        json.dump({"GAME_PATH": ""}, f)

root = tk.Tk()
root.withdraw()

with open(config_path, "r") as f:
    config = json.load(f)

game_path = config.get("GAME_PATH","")

if not game_path or game_path == "":
    flag = True
    while(flag):
        input("BLEACH_Rebirth_of_Souls.exe not found. You can find it in your steam folder. Press Enter to select it...")
        game_path = filedialog.askopenfilename(title="Select Bleach rebirth of souls",filetypes=[("Executable files", "*.exe")])

        if"BLEACH_Rebirth_of_Souls.exe" in game_path:
            flag = False

    parent_dir = os.path.dirname(game_path)
    game_path = str(parent_dir)
    config["GAME_PATH"] = game_path
    with open(config_path, "w") as f:
        json.dump(config, f)
    

choice = -1

while choice not in [1, 2, 6]:
    try:
        print("\nCurrent Bleach Rebirth of Souls folder:", game_path)

        choice = int(input(f"""

(1) : Launch Bleach Rebirth of Souls
(2) : Launch Bleach Rebirth of Souls Community Patch
(3) : Change game path
(4) : Read balance changes
(5) : Keep default osts on the Community Patch ( currently : {config["DEFAULT_OST"]} )
(6) : Exit

Choose one of the options :  """))
    except:
        choice = -1

    if choice == 3:
        flag = True
        firstTime = True
        while(flag):
            if not firstTime:
                input("BLEACH_Rebirth_of_Souls.exe not found. You can find it in your steam folder. Press Enter to select it...")
            game_path = filedialog.askopenfilename(title="Select Bleach rebirth of souls",filetypes=[("Executable files", "*.exe")])

            if"BLEACH_Rebirth_of_Souls.exe" in game_path:
                flag = False
            elif firstTime:
                firstTime = False

        parent_dir = os.path.dirname(game_path)
        game_path = str(parent_dir)
        config["GAME_PATH"] = game_path

        with open(config_path, "w") as f:
            json.dump(config, f)

    if choice == 4:
        balance_file = os.path.join(BASE_DIR, "BalanceChanges/LatestChanges.txt")
        if os.path.exists(balance_file):
            os.startfile(balance_file)
        else:
            print("BalanceChanges.txt not found")

    if choice == 5:
        if config["DEFAULT_OST"] == "ON":
            config["DEFAULT_OST"] = "OFF"
        else:
            config["DEFAULT_OST"] = "ON"

        with open(config_path,"w") as f:
            json.dump(config,f)

    if choice == 6:
        exit()

files = ""

if choice == 1:
    files = "Bros"
elif choice == 2:
    files = "BrosCommunityEdition"

try:
    action_src = os.path.join(BASE_DIR, f"{files}Files", "Action")
    action_dst = os.path.join(game_path, "Script", "Action")

    shutil.copytree(action_src, action_dst, dirs_exist_ok=True)

    shutil.copy(
        os.path.join(BASE_DIR, f"{files}Files", "CharaStatus.fsv"),
        os.path.join(game_path, "Script")
    )

    shutil.copy(
        os.path.join(BASE_DIR, f"{files}Files", "CommonParam.fsv"),
        os.path.join(game_path, "Script")
    )

    if config["DEFAULT_OST"] == "ON":
        files = "Bros"
    
    shutil.copy(
        os.path.join(BASE_DIR, f"{files}Files", "bgm.bnk"),
        os.path.join(game_path, "Sound")
    )
    

except Exception as e:
    print("Error copying files:", e)

try:
    os.startfile("steam://rungameid/1689620")
except Exception as e:
    print("Error launching game:", e)