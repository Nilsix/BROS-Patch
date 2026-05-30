import tkinter as tk
import json
from tkinter import filedialog
import shutil
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "config.json")
updated = False
try:
    result = subprocess.run(["git", "-C", BASE_DIR, "pull"], check=True, capture_output=True, text=True)
    output = result.stdout.strip()
    if "Already up to date." in output:
        print("Mod is already up to date.")
    else:
        print("Mod updated successfully.")
        updated = True

except Exception as e:
    print("Git update failed:", e)

if not os.path.exists(config_path):
    with open(config_path, "w") as f:
        json.dump({"GAME_PATH": ""}, f)

root = tk.Tk()
root.withdraw()

with open(config_path, "r") as f:
    config = json.load(f)

game_path = config.get("GAME_PATH", "")

if not game_path or game_path == "":
    input("Game Path not found. Press Enter to select it...")
    game_path = filedialog.askdirectory()
    config["GAME_PATH"] = game_path

    with open(config_path, "w") as f:
        json.dump(config, f)

choice = -1

while choice not in [1, 2, 5]:
    try:
        print("Make sure you got the right game path (Bleach Rebirth of Souls folder), otherwise the mod won't work. If you want to change it, select option 3.")
        print("\nCurrent Bleach Rebirth of Souls path:", game_path)

        choice = int(input("""
(1) : Launch Bleach Rebirth of Souls
(2) : Launch Bleach Rebirth of Souls Community Edition
(3) : Change game path
(4) : Read balance changes
(5) : Exit
> """))
    except:
        choice = -1

    if choice == 3:
        game_path = filedialog.askdirectory()
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

except Exception as e:
    print("Error copying files:", e)

try:
    os.startfile("steam://rungameid/1689620")
except Exception as e:
    print("Error launching game:", e)