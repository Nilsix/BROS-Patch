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
import sys
from pathlib import Path

pygameInstallSucess = False
try: 
    import pygame
except :
    subprocess.run(
        [sys.executable,"-m","pip","install","pygame"]
    )
    try:
        import pygame
    except:
        pass

try: 
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
   
    template_path = os.path.join(BASE_DIR,"Json","configTemplate.json")
    config_path = os.path.join(BASE_DIR,"Json","config.json")
    if not os.path.exists(config_path):
        shutil.copy(template_path,config_path)
    else:
        with open(template_path, "r",encoding="utf-8") as f:
            data1 = json.load(f)
        with open(config_path,"r",encoding="utf-8") as f:
            data2 = json.load(f)
        if len(data1) != len(data2):
            shutil.copy(template_path,config_path)
    config_path = os.path.join(BASE_DIR,"Json","config.json")

    with open(config_path, "r") as f:
        config = json.load(f)
    
    if config["MAINTENANCE"] != "LITERALLY_SHOWING_THE_PW_IN_THE_CODE":
        input("The launcher is going under maintenance for several hours")
        exit()
    
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
    gameMode = "DEFAULT"
     
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
    launcherOstPath = os.path.join(ressourcesPath,"LauncherOst.wav")
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(launcherOstPath)
        pygame.mixer.music.play(loops=-1)
    except:
        winsound.PlaySound(launcherOstPath,winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
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
            action_src = os.path.join(BASE_DIR,"GameVersions",f"{files}",f'{folderName}')
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
            pygame.mixer.music.stop()
        except:
            pass
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

        

            shutil.copytree(os.path.join(BASE_DIR,"Files","Spec Mod",'reverse_globe_effect_remover_by_grifo',f'{config["reverse_globe_effect_remover_by_grifo"]}',"high"),
                        os.path.join(game_path,"00HIGH","Effect","spfx","com"),dirs_exist_ok=True)
            
            shutil.copytree(os.path.join(BASE_DIR,"Files","Spec Mod",'reverse_globe_effect_remover_by_grifo',f'{config["reverse_globe_effect_remover_by_grifo"]}',"middle"),
                        os.path.join(game_path,"01MIDDLE","Effect","spfx","com"),dirs_exist_ok=True)
            
            for folder in os.listdir(os.path.join(BASE_DIR,"Files","Spec Mod")):
                injectOstFiles(folder,config[folder])
            

            #gamemode injection
            if gameMode != "Default":
                srcPath = os.path.join(BASE_DIR,"Game Modes",f"{gameMode}")
                dstPath = os.path.join(game_path,"Script")
                
                if os.path.exists(os.path.join(srcPath,"CharaStatus.fsv")):
                    shutil.copy(
                        os.path.join(srcPath,"CharaStatus.fsv"),
                        os.path.join(dstPath,"CharaStatus.fsv"))
            
            #team battle injection
            if config["TEAM_BATTLE"] == "ON":
                srcPath = os.path.join(BASE_DIR,"Game Modes","TeamBattle")
                dstPath = os.path.join(game_path,"Script")   
                shutil.copy(
                    os.path.join(srcPath,"CharaStatus.fsv"),
                    os.path.join(dstPath,"CharaStatus.fsv"))
        

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
        creditsFile = os.path.join(BASE_DIR,"Credits","credits.txt")
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
        
   
    def gameModesMenu():
        gameModesPage.tkraise()

    

    #box
    container = Frame(window, bg=bgcolor)
    container.pack(expand=YES)
    mainPage = Frame(container,bg=bgcolor)
    settingsPage = Frame(container,bg=bgcolor)
    gameModesPage = Frame(container,bg=bgcolor)

    #labels
    labelTitle = Label(mainPage, text="Bleach Rebirth of Souls community patch launcher", font=("Arial",30),bg=bgcolor,fg=labelcolor)
    labelSubTitle = Label(mainPage,text="made by Nilsix :3",font=("Courrier",20),bg=bgcolor,fg=labelcolor)
    labelTitleSettings = Label(settingsPage, text="Bleach Rebirth of Souls community patch launcher", font=("Arial",30),bg=bgcolor,fg=labelcolor)
    labelSubTitleSettings = Label(settingsPage,text="made by Nilsix :3",font=("Courrier",20),bg=bgcolor,fg=labelcolor)
    labelTitleGameModes = Label(gameModesPage, text="Bleach Rebirth of Souls community patch launcher", font=("Arial",30),bg=bgcolor,fg=labelcolor)
    labelSubTitleGameModes = Label(gameModesPage,text="made by Nilsix :3",font=("Courrier",20),bg=bgcolor,fg=labelcolor)
    labelGamePath = Label(mainPage,text=f'Current game path : {game_path}',font=("Courrier",15),bg=bgcolor,fg=labelcolor)
    brosVersion = StringVar()
    gameVersionsList = []
    gameVersionsPath = os.path.join(BASE_DIR,"GameVersions")
    for folder in os.listdir(gameVersionsPath):
            gameVersionsList.append(folder)
    brosVersionList = ttk.Combobox(
        mainPage,
        textvariable=brosVersion,
        values=gameVersionsList,
        state="readonly",
        font=("Courrier",25)
    )

    brosVersionList.set("Choose a game version")

    def preLauncher():
        if brosVersionList.get() != "Choose a game version":
            launch(brosVersionList.get())
        
    def performanceSettingsMenu():
        settingsPage.tkraise()

    def adjustAwakeningAuraSettings():
        if config["awakeningaura_effects_by_grifo"] == "original":
            config["awakeningaura_effects_by_grifo"] = "lowspec"
        else:
            config["awakeningaura_effects_by_grifo"] = "original"
        awakeningAuraButton.config(text=f'remove awakening aura : currently {"OFF" if config["awakeningaura_effects_by_grifo"] == "original" else "ON"}')
    
    def adjustBreakerGrabSettings():
        if config["breaker_grab_effect_remover_by_grifo"] == "original":
            config["breaker_grab_effect_remover_by_grifo"] = "lowspec"
        else:
            config["breaker_grab_effect_remover_by_grifo"] = "original"

        breakerGrabButton.config(
            text=f'remove breaker grab effect : currently {"OFF" if config["breaker_grab_effect_remover_by_grifo"] == "original" else "ON"}'
        )
    def adjustHakugekiSettings():
        if config["hakugeki_effect_remover_by_grifo"] == "original":
            config["hakugeki_effect_remover_by_grifo"] = "lowspec"
        else:
            config["hakugeki_effect_remover_by_grifo"] = "original"
        hakugekiButton.config(text=f'remove hakugeki effect : currently {"OFF" if config["hakugeki_effect_remover_by_grifo"] == "original" else "ON"}')
    
    def adjustHitEffectSettings():
        if config["hit_effect_remover_by_grifo"] == "original":
            config["hit_effect_remover_by_grifo"] = "lowspec"
        else:
            config["hit_effect_remover_by_grifo"] = "original"
        hitEffectButton.config(text=f'remove hit effect : currently {"OFF" if config["hit_effect_remover_by_grifo"] == "original" else "ON"}')  
    
    def adjustReverseGlobeSettings():
        if config["reverse_globe_effect_remover_by_grifo"] == "original":
            config["reverse_globe_effect_remover_by_grifo"] = "lowspec"
        else:
            config["reverse_globe_effect_remover_by_grifo"] = "original"
        reverseGlobeButton.config(text=f'remove reverse globe effect : currently {"OFF" if config["reverse_globe_effect_remover_by_grifo"] == "original" else "ON"}')  
    
    def adjustSkillActivationSettings():
        if config["skill_activation_effect_remover_by_grifo"] == "original":
            config["skill_activation_effect_remover_by_grifo"] = "lowspec"
        else:
            config["skill_activation_effect_remover_by_grifo"] = "original"
        skillActivationButton.config(text=f'remove skill activation effect : currently {"OFF" if config["skill_activation_effect_remover_by_grifo"] == "original" else "ON"}')  

    def backToMainMenu():
        mainPage.tkraise()
    
    def baseOnlyFunc():
        global gameMode
        if gameMode == "BaseOnly":
            gameMode = "DEFAULT"
        else:
            gameMode = "BaseOnly"
        baseOnlyButton.config(text=f'Base Only : (Currently {"ON" if gameMode == "BaseOnly" else "OFF"})')
    
    def teamBattleFunc():
        with open(config_path,"w") as f:
            config["TEAM_BATTLE"] = "ON" if config["TEAM_BATTLE"] == "OFF" else "OFF"
            json.dump(config,f)
        teamBattleButton.config(text=f'Team Battle : (Currently {"ON" if config["TEAM_BATTLE"] == "ON" else "OFF"})')

    textSize = 18
    paddingYvalue = 15
    #buttons
    launchButton = Button(mainPage,text="Launch the game",font=("Courrier",textSize),bg="white",fg=bgcolor,command=preLauncher)
    launchBrosButton = Button(mainPage,text="Launch Bleach Rebirth of Souls",font=("Courrier",textSize),bg="white",fg=bgcolor,command=lambda : launch("Bros"))
    launchBrosPatchButton =  Button(mainPage,text=f'Launch Bleach Rebirth of Souls Community Patch',font=("Courrier",textSize),bg="white",fg=bgcolor,command=lambda : launch("BrosCommunityPatch"))
    changeGamePathButton =  Button(mainPage,text=f'Change your game path',font=("Courrier",textSize),bg="white",fg=bgcolor,command=changeGamePath)
    readBalanceChangesButton =  Button(mainPage,text=f'Read balance changes',font=("Courrier",textSize),bg="white",fg=bgcolor,command=readBalanceChanges)
    ostSettingsButton =  Button(mainPage,text=f'OST Mod :  ( currently : {config["OST_MOD"]} )',font=("Courrier",textSize),bg="white",fg=bgcolor,command=lambda: ostSettings(ostSettingsButton))
    lowSpecButton =  Button(mainPage,text=f'FPS Booster settings',font=("Courrier",textSize),bg="white",fg=bgcolor,command=performanceSettingsMenu)
    CreditsButton = Button(mainPage,text="Credits",font=("Courrier",textSize),bg="white",fg=bgcolor,command=readCredits)
    gameModesButton = Button(mainPage,text="Game Modes",font=("Courrier",textSize),bg="white",fg=bgcolor,command=gameModesMenu)
    



    #pack
    labelTitle.pack()
    labelSubTitle.pack()
    labelGamePath.pack(pady=paddingYvalue,fill=X)
    brosVersionList.pack(pady=paddingYvalue,fill=X)
    launchButton.pack()
    changeGamePathButton.pack(pady=paddingYvalue,fill=X)
    readBalanceChangesButton.pack(pady=paddingYvalue,fill=X)
    gameModesButton.pack(pady=paddingYvalue,fill=X)
    ostSettingsButton.pack(pady=paddingYvalue,fill=X)
    lowSpecButton.pack(pady=paddingYvalue,fill=X)
    CreditsButton.pack(pady=paddingYvalue,fill=X)


    labelTitleSettings.pack()
    labelSubTitleSettings.pack()


    #Settings page
    awakeningAuraButton = Button(
    settingsPage,
    text=f'remove awakening aura : currently {"OFF" if config["awakeningaura_effects_by_grifo"] == "original" else "ON"}',
    font=("Courrier", textSize),
    bg="white",
    fg=bgcolor,
    command=adjustAwakeningAuraSettings
)
    awakeningAuraButton.pack(pady=paddingYvalue, fill=X)


    breakerGrabButton = Button(
        settingsPage,
        text=f'remove breaker grab effect : currently {"OFF" if config["breaker_grab_effect_remover_by_grifo"] == "original" else "ON"}',
        font=("Courrier", textSize),
        bg="white",
        fg=bgcolor,
        command=adjustBreakerGrabSettings
    )
    breakerGrabButton.pack(pady=paddingYvalue, fill=X)


    hakugekiButton = Button(
        settingsPage,
        text=f'remove hakugeki effect : currently {"OFF" if config["hakugeki_effect_remover_by_grifo"] == "original" else "ON"}',
        font=("Courrier", textSize),
        bg="white",
        fg=bgcolor,
        command=adjustHakugekiSettings
    )
    hakugekiButton.pack(pady=paddingYvalue, fill=X)


    hitEffectButton = Button(
        settingsPage,
        text=f'remove hit effect : currently {"OFF" if config["hit_effect_remover_by_grifo"] == "original" else "ON"}',
        font=("Courrier", textSize),
        bg="white",
        fg=bgcolor,
        command=adjustHitEffectSettings
    )
    hitEffectButton.pack(pady=paddingYvalue, fill=X)


    reverseGlobeButton = Button(
        settingsPage,
        text=f'remove reverse globe effect : currently {"OFF" if config["reverse_globe_effect_remover_by_grifo"] == "original" else "ON"}',
        font=("Courrier", textSize),
        bg="white",
        fg=bgcolor,
        command=adjustReverseGlobeSettings
    )
    reverseGlobeButton.pack(pady=paddingYvalue, fill=X)


    skillActivationButton = Button(
        settingsPage,
        text=f'remove skill activation effect : currently {"OFF" if config["skill_activation_effect_remover_by_grifo"] == "original" else "ON"}',
        font=("Courrier", textSize),
        bg="white",
        fg=bgcolor,
        command=adjustSkillActivationSettings 
    )
    skillActivationButton.pack(pady=paddingYvalue, fill=X)
    
    mainMenuButton = Button(
        settingsPage,
        text="Main Menu",
        font=("Courrier", textSize),
        bg="white",
        fg=bgcolor,
        command=backToMainMenu
    )

    mainMenuButton.pack(pady=paddingYvalue,fill=X)

    #game modes page
    labelTitleGameModes.pack(pady=paddingYvalue)
    labelSubTitleGameModes.pack(pady=paddingYvalue)

    gameModesMenuButton = Button(
        gameModesPage,
        text="Main Menu",
        font=("Courrier", textSize),
        bg="white",
        fg=bgcolor,
        command=backToMainMenu
    )

    baseOnlyButton = Button(
        gameModesPage,
        text=f'Base Only : (Currently {"ON" if gameMode == "BaseOnly" else "OFF"})',
        font=("Courrier", textSize),
        bg="white",
        fg=bgcolor,
        command=baseOnlyFunc
    )

    teamBattleButton = Button(
        gameModesPage,
        text=f'Team Battle : (Currently {"ON" if config["TEAM_BATTLE"] == "ON" else "OFF"})',
        font=("Courrier", textSize),
        bg="white",
        fg=bgcolor,
        command=teamBattleFunc
    )

    teamBattleButton.pack(pady=paddingYvalue, fill=X)
    baseOnlyButton.pack(pady=paddingYvalue, fill=X)
    gameModesMenuButton.pack(pady=paddingYvalue, fill=X)
    
   
    for page in(mainPage,settingsPage,gameModesPage):
        page.grid(row=0,column=0,sticky="nsew")
    mainPage.tkraise()

    window.mainloop()
except Exception as e:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)
    print(e)
    input("ping the error to Nilsix")
