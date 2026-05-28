import tkinter as tk
import json 
from tkinter import filedialog
import shutil
import os
import subprocess


try:
    subprocess.run(["git", "pull", "https://github.com/Nilsix/BROS-Community-Patch.git"])
except Exception as e:
    print("Error pulling the latest changes: make sure you followed the instruction on README.md")

root = tk.Tk()
root.withdraw()
config_path = "config.json"
with open(config_path,"r") as f:
    config = json.load(f)
game_path = config.get("GAME_PATH")

if not game_path or game_path == "":
    chooseFolder = input("Game Path not found, choose your Bleach Rebirth of Souls folder, it can be found in your Steam library (Press Enter to continue)")   
    game_path = filedialog.askdirectory()
    config["GAME_PATH"] = game_path
    with open(config_path,"w") as f:
        json.dump(config,f)
choice = -1
while choice != 1 and choice != 2:
    try: 
        print("Current Bleach Rebirth of Souls path: ",game_path)
        choice = int(input("""(1) : Launch Bleach Rebirth of Souls 
(2) : Launch Bleach Rebirth of Souls Community Edition 
(3) : Change game path
(4) Read balance changes
(5) : Exit
: """))
    except:
        choice = -1
    if(choice == 3):
        game_path = filedialog.askdirectory()
        config["GAME_PATH"] = game_path
        with open(config_path,"w") as f:
            json.dump(config,f)
    if (choice == 4):
        os.startfile("BalanceChanges.txt")
    if(choice == 5):
        exit()


files = ""
if choice == 1:
    files = "Bros"
if choice == 2:
    files = "BrosCommunityEdition"


shutil.copytree(f"{files}Files\\Action", f"{game_path}\\Script\\Action", dirs_exist_ok=True)
shutil.copy(f"{files}Files\\CharaStatus.fsv", f"{game_path}\\Script")
shutil.copy(f"{files}Files\\CommonParam.fsv", f"{game_path}\\Script")

try:
    os.startfile("steam://rungameid/1689620")
except Exception as e:
    print("Error launching the game: ", e)


    

    