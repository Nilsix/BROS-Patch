from tkinter import * 
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import json
import shutil
import os
import subprocess
import ctypes
import winsound
from pathlib import Path




try: 
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    window = Tk()
    
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)  
    window.title("Bleach Community Patch")
    window.geometry("1080x800")
    window.iconbitmap(os.path.join(BASE_DIR,"ressources/pimplin.ico"))
    #minimum size of the window
    window.minsize(480,360)
    bgcolor = "#4A1942"
    labelcolor = "#D9B8D4"
    window.config(background=bgcolor)
     
    try:
        result = subprocess.run(["git", "-C", BASE_DIR, "pull"], check=True, capture_output=True, text=True)
        output = result.stdout.strip()
        if "Already up to date." in output:
            pass
        
        #if there is an update, will relaunch the launcher so the code actually gets reset too
        else:
            subprocess.run(os.path.join(BASE_DIR,"Bleach Rebirth of Souls Community Patch.py"),shell=True)
            winsound.PlaySound(None,winsound.SND_PURGE)
            exit()

    except Exception as e:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)
        print("Git update failed :", e)
        print("Please delete this folder and redo the installation, while installing make sure to wait for the installer window to close itself, DO NOT close it yourself even if you see 'done' written on the installation window")
        a = input("Press Enter to exit ")

        exit()

    ressourcesPath = os.path.join(BASE_DIR,"ressources")
    winsound.PlaySound(os.path.join(ressourcesPath,"LauncherOst.wav"),winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)

    try :
        template_path = os.path.join(BASE_DIR,"configTemplate.json")
        config_path = os.path.join(BASE_DIR,"config.json")
        if not os.path.exists(config_path):
            shutil.copy(template_path,config_path)
        else:
            with open(template_path, "r",encoding="utf-8") as f:
                data1 = json.load(f)
            with open(config_path,"r",encoding="utf-8") as f:
                data2 = json.load(f)
            if len(data1) != len(data2):
                shutil.copy(template_path,config_path)

    except Exception as e: 
        print(e)
    config_path = os.path.join(BASE_DIR, "config.json")

    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump({"GAME_PATH": ""}, f)






    with open(config_path, "r") as f:
        config = json.load(f)
        

    game_path = config.get("GAME_PATH","")

    if not game_path or game_path == "" or not "BLEACH Rebirth of Souls" in game_path:
        flag = True
        while(flag):
            messagebox.showinfo("Bleach not found","BLEACH_Rebirth_of_Souls.exe not found. You can find it in your steam folder, press ok then select it")
            game_path = filedialog.askopenfilename(title="Select Bleach rebirth of souls",filetypes=[("Executable files", "*.exe")])

            if"BLEACH_Rebirth_of_Souls.exe" in game_path:
                flag = False

        parent_dir = os.path.dirname(game_path)
        game_path = str(parent_dir)
        config["GAME_PATH"] = game_path
        with open(config_path, "w") as f:
            json.dump(config, f)


    def injectFolder(files,folderName):
            action_src = os.path.join(BASE_DIR,"Files",f"{files}",f'{folderName}')
            action_dst = os.path.join(game_path,f'{folderName}')
            shutil.rmtree(action_dst)
            shutil.copytree(action_src, action_dst)

    def injectOstFiles(folderName,lowspecmodornot):
        shutil.copytree(os.path.join(BASE_DIR,"Files","Spec Mod",f'{folderName}',f'{lowspecmodornot}'),
                        os.path.join(game_path,"00HIGH","Effect","spfx","com"),dirs_exist_ok=True)
        shutil.copytree(os.path.join(BASE_DIR,"Files","Spec Mod",f'{folderName}',f'{lowspecmodornot}'),
                        os.path.join(game_path,"01MIDDLE","Effect","spfx","com"),dirs_exist_ok=True)
    
    
    def launch(files):
        window.destroy()
        try:
            #folder injection
            injectFolder(files,"Script")

            #ost choice
            if config["OST_MOD"] == "ON":
                files = "Mod"
            else : 
                files = "Default"
            shutil.copy(
                os.path.join(BASE_DIR,"Files","OST",f"{files}", "bgm.bnk"),
                os.path.join(game_path, "Sound")
            )

            #Low Spec mode
            lowSpecFolder = ""
            if config["LOW_SPEC_MODE"] == "ON":
                lowSpecFolder = "lowspec"
            else:
                lowSpecFolder = "original"

            shutil.copytree(os.path.join(BASE_DIR,"Files","Spec Mod",'reverse_globe_effect_remover_by_grifo',f'{lowSpecFolder}',"high"),
                        os.path.join(game_path,"00HIGH","Effect","spfx","com"),dirs_exist_ok=True)
            
            shutil.copytree(os.path.join(BASE_DIR,"Files","Spec Mod",'reverse_globe_effect_remover_by_grifo',f'{lowSpecFolder}',"middle"),
                        os.path.join(game_path,"01MIDDLE","Effect","spfx","com"),dirs_exist_ok=True)
            
            injectOstFiles("awakeningaura_effects_by_grifo",lowSpecFolder)
            injectOstFiles("breaker_grab_effect_remover_by_grifo",lowSpecFolder)
            injectOstFiles("hakugeki_effect_remover_by_grifo",lowSpecFolder)
            injectOstFiles("hit_effect_remover_by_grifo",lowSpecFolder)
            injectOstFiles("skill_activation_effect_remover_by_grifo",lowSpecFolder)
            

        
        except Exception as e:
            print("Error copying files:", e)

        forlater = """
        else:
            src = Path(os.path.join(BASE_DIR,"Files",choice))
            dst = Path(game_path)

            dst.mkdir(parents=True,exist_ok=True)

            for item in src.rglob("*"):
                if item.is_file:
                    relative_path = item.relative_to(src)
                    target_file = dst / relative_path

                    target_file.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(item,target_file)
            """

        try:
            os.startfile("steam://rungameid/1689620")
        except Exception as e:
            print("Error launching game:", e)
        

    def readBalanceChanges():
        balance_file = os.path.join(BASE_DIR, "BalanceChanges/LatestChanges.txt")
        if os.path.exists(balance_file):
            os.startfile(balance_file)
        else:
            print("BalanceChanges.txt not found")
    
    def readCredits():
        creditsFile = os.path.join(BASE_DIR, "credits.txt")
        if os.path.exists(creditsFile):
            os.startfile(creditsFile)

    def ostSettings(button):
        if config["OST_MOD"] == "ON":
            config["OST_MOD"] = "OFF"
        else:
            config["OST_MOD"] = "ON"

        with open(config_path,"w") as f:
            json.dump(config,f)
        button.config(text=f'OST Mod : ( currently : {config["OST_MOD"]} )')

    def changeGamePath():
        flag = True
        firstTime = True
        while(flag):
            game_path = filedialog.askopenfilename(title="Select Bleach rebirth of souls",filetypes=[("Executable files", "*.exe")])
            if"BLEACH_Rebirth_of_Souls.exe" in game_path:
                flag = False
            elif firstTime:
                firstTime = False
                messagebox.showerror("Error","BLEACH_Rebirth_of_Souls.exe not found")
                

        parent_dir = os.path.dirname(game_path)
        game_path = str(parent_dir)
        config["GAME_PATH"] = game_path

        with open(config_path, "w") as f:
            json.dump(config, f)
        
    def lowSpecFunc(button):
        if config["LOW_SPEC_MODE"] == "ON":
            config["LOW_SPEC_MODE"] = "OFF"
        else:
            config["LOW_SPEC_MODE"] = "ON"

        with open(config_path,"w") as f:
            json.dump(config,f)
        button.config(text=f'Low Spec Mod : ( currently : {config["LOW_SPEC_MODE"]} )')
    

    

    #box
    frame = Frame(window, bg=bgcolor)

    #labels
    labelTitle = Label(frame, text="Bleach Rebirth of Souls community patch launcher", font=("Arial",30),bg=bgcolor,fg=labelcolor)
    labelSubTitle = Label(frame,text="made by Nilsix :3",font=("Courrier",20),bg=bgcolor,fg=labelcolor)
    labelGamePath = Label(frame,text=f'Current game path : {game_path}',font=("Courrier",15),bg=bgcolor,fg=labelcolor)
    brosVersion = StringVar()
    brosVersionList = ttk.Combobox(
        frame,
        textvariable=brosVersion,
        values=["Bleach Rebirth of Souls","Bleach Rebirth of Souls Community Patch","Bros 1.40 (Big Yuha release patch)","Old Bros Test"],
        state="readonly",
        font=("Courrier",25)
    )

    brosVersionList.set("Choose a game version")

    def preLauncher():
        if brosVersionList.get() != "Choose a game version":
            launch(brosVersionList.get())

    textSize = 20
    paddingYvalue = 15
    #buttons
    launchButton = Button(frame,text="Launch the game",font=("Courrier",textSize),bg="white",fg=bgcolor,command=preLauncher)
    launchBrosButton = Button(frame,text="Launch Bleach Rebirth of Souls",font=("Courrier",textSize),bg="white",fg=bgcolor,command=lambda : launch("Bros"))
    launchBrosPatchButton =  Button(frame,text=f'Launch Bleach Rebirth of Souls Community Patch',font=("Courrier",textSize),bg="white",fg=bgcolor,command=lambda : launch("BrosCommunityPatch"))
    changeGamePathButton =  Button(frame,text=f'Change your game path',font=("Courrier",textSize),bg="white",fg=bgcolor,command=changeGamePath)
    readBalanceChangesButton =  Button(frame,text=f'Read balance changes',font=("Courrier",textSize),bg="white",fg=bgcolor,command=readBalanceChanges)
    ostSettingsButton =  Button(frame,text=f'OST Mod :  ( currently : {config["OST_MOD"]} )',font=("Courrier",textSize),bg="white",fg=bgcolor,command=lambda: ostSettings(ostSettingsButton))
    lowSpecButton =  Button(frame,text=f'Low Spec Mode :  ( currently : {config["LOW_SPEC_MODE"]} )',font=("Courrier",textSize),bg="white",fg=bgcolor,command=lambda: lowSpecFunc(lowSpecButton))
    CreditsButton = Button(frame,text="Credits",font=("Courrier",textSize),bg="white",fg=bgcolor,command=readCredits)
    

    #pack
    labelTitle.pack()
    labelSubTitle.pack()
    labelGamePath.pack(pady=paddingYvalue,fill=X)
    brosVersionList.pack(pady=paddingYvalue,fill=X)
    launchButton.pack()
    changeGamePathButton.pack(pady=paddingYvalue,fill=X)
    readBalanceChangesButton.pack(pady=paddingYvalue,fill=X)
    ostSettingsButton.pack(pady=paddingYvalue,fill=X)
    lowSpecButton.pack(pady=paddingYvalue,fill=X)
    CreditsButton.pack(pady=paddingYvalue,fill=X)

    frame.pack(expand=YES)


    window.mainloop()
except Exception as e:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)
    print(e)
    input("ping the error to Nilsix")
