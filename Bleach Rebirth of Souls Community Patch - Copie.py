from tkinter import * 
import json
from tkinter import filedialog
import shutil
import os
import subprocess
import ctypes

#yeah I know I stored the password here so you can just find it here, I know I could use an hash or crypt it but I just didn't bother it ain't sensitive data
#I know you can also just change the config.json and change the flag to true but like I said I didn't bother
#I also know mfs aren't gonna bother reading the py file and if they did bother then they deserve to have the pass ig
fakofeaopkeg = "aINSGi14iEoGPzhv"


try: 
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    try:
        result = subprocess.run(["git", "-C", BASE_DIR, "pull"], check=True, capture_output=True, text=True)
        output = result.stdout.strip()
        #if "Already up to date." in output:
            #print("Mod is already up to date.")
        #else:
            #print("Mod updated successfully.")
    except Exception as e:
        print("Git update failed :", e)
        print("Please delete this folder and redo the installation, while installing make sure to wait for the installer window to close itself, DO NOT close it yourself even if you see 'done' written on the installation window")
        a = input("Press Enter to exit ")
        exit()




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






    with open(config_path, "r") as f:
        config = json.load(f)


    password = False
    if config["kpkp"] == "BANANA":
        password = True
        
        
    while not password:
        theNpass = input("Enter password : ")
        if theNpass == fakofeaopkeg:
            password = True
            config["kpkp"] = "BANANA"
            with open(config_path, "w") as f:
                json.dump(config, f)
        

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
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)   
    window= Tk()

    files = ""
    def launch(choice):
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
        window.destroy()

    def readBalanceChanges():
        balance_file = os.path.join(BASE_DIR, "BalanceChanges/LatestChanges.txt")
        if os.path.exists(balance_file):
            os.startfile(balance_file)
        else:
            print("BalanceChanges.txt not found")

    def ostSettings(button):
        if config["DEFAULT_OST"] == "ON":
            config["DEFAULT_OST"] = "OFF"
        else:
            config["DEFAULT_OST"] = "ON"

        with open(config_path,"w") as f:
            json.dump(config,f)
        button.config(text=f'Keep default osts on the Community Patch ( currently : {config["DEFAULT_OST"]} )')

    def changeGamePath():
        flag = True
        firstTime = True
        while(flag):
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


    window.title("Bleach Community Patch")
    window.geometry("1080x720")
    window.iconbitmap(os.path.join(BASE_DIR,"ressources/pimplin.ico"))
    #minimum size of the window
    window.minsize(480,360)
    bgcolor = "#4A1942"
    labelcolor = "#D9B8D4"
    window.config(background=bgcolor)

    #box
    frame = Frame(window, bg=bgcolor)

    #labels
    labelTitle = Label(frame, text="Bleach Rebirth of Souls community patch launcher", font=("Arial",30),bg=bgcolor,fg=labelcolor)
    labelSubTitle = Label(frame,text="made by Nilsix :3",font=("Courrier",20),bg=bgcolor,fg=labelcolor)
    labelGamePath = Label(frame,text=f'Current game path : {game_path}',font=("Courrier",15),bg=bgcolor,fg=labelcolor)

    #buttons
    launchBrosButton = Button(frame,text="Launch Bleach Rebirth of Souls",font=("Courrier",25),bg="white",fg=bgcolor,command=lambda : launch(1))
    launchBrosPatchButton =  Button(frame,text=f'Launch Bleach Rebirth of Souls Community Patch',font=("Courrier",25),bg="white",fg=bgcolor,command=lambda : launch(2))
    changeGamePathButton =  Button(frame,text=f'Change your game path',font=("Courrier",25),bg="white",fg=bgcolor,command=changeGamePath)
    readBalanceChangesButton =  Button(frame,text=f'Read balance changes',font=("Courrier",25),bg="white",fg=bgcolor,command=readBalanceChanges)
    ostSettingsButton =  Button(frame,text=f'Keep default osts on the Community Patch ( currently : {config["DEFAULT_OST"]} )',font=("Courrier",25),bg="white",fg=bgcolor,command=lambda: ostSettings(ostSettingsButton))

    #pack
    labelTitle.pack()
    labelSubTitle.pack()
    labelGamePath.pack(pady=10)
    launchBrosButton.pack(pady=25,fill=X)
    launchBrosPatchButton.pack(pady=25,fill=X)
    changeGamePathButton.pack(pady=25,fill=X)
    readBalanceChangesButton.pack(pady=25,fill=X)
    ostSettingsButton.pack(pady=25,fill=X)


    frame.pack(expand=YES)


    window.mainloop()
except Exception as e:
    print(e)
    input("stop")
