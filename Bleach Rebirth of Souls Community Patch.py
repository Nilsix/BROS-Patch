from tkinter import * 
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import json
import shutil
import os
import subprocess   
import platform
try :
    import ctypes
except:
    pass
try:
    import winsound
except:
    pass
import sys
import webbrowser
from pathlib import Path

# pygame is bundled inside the launcher binary; if it is somehow missing we
# just run without music rather than trying to pip-install it.
try:
    import pygame
except Exception:
    pygame = None


try: 
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # The bundled launcher (bootstrap) already syncs this folder to the latest
    # version before we start, so there is no git/pull step here any more.
    # We just expose a helper so the in-app buttons can fetch updates on demand.
    sys.path.insert(0, BASE_DIR)
    try:
        import updater
    except Exception:
        updater = None

    def pull_latest():
        """Fetch the newest patch files over HTTPS (no git needed).
        Returns True on success, False otherwise."""
        if updater is None:
            return False
        try:
            updater.update(BASE_DIR)
            return True
        except Exception as e:
            print("Update failed:", e)
            return False

    def open_file(path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
   
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
    
    window = Tk()
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)  
    except:
        pass
    window.title("Bleach Community Patch")
    window.geometry("1080x860")
    window.iconbitmap(os.path.join(BASE_DIR,"ressources/pimplin.ico"))
    #minimum size of the window
    window.minsize(480,360)
    bgcolor = "#4A1942"
    labelcolor = "#D9B8D4"
    window.config(background=bgcolor)
    gameMode = "DEFAULT"

    # ── Hover helpers ──────────────────────────────────────────────────────────
    HOVER_BG   = "#F5D6F0"   # light lilac highlight on mouse-over
    NORMAL_BG  = "white"

    class Tooltip:
        """Small pop-up label that appears after the mouse rests on a widget."""
        DELAY_MS = 700          # how long the cursor must stay still before appearing

        def __init__(self, widget, text):
            self.widget  = widget
            self.text    = text
            self._job    = None
            self._tip_wnd = None
            widget.bind("<Enter>",    self._schedule, add="+")
            widget.bind("<Leave>",    self._cancel,   add="+")
            widget.bind("<ButtonPress>", self._cancel, add="+")

        def _schedule(self, event=None):
            self._cancel()
            self._job = self.widget.after(self.DELAY_MS, self._show)

        def _cancel(self, event=None):
            if self._job:
                self.widget.after_cancel(self._job)
                self._job = None
            self._hide()

        def _show(self):
            if self._tip_wnd:
                return
            x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
            self._tip_wnd = tw = Toplevel(self.widget)
            tw.wm_overrideredirect(True)          # no title bar / borders
            tw.wm_geometry(f"+{x}+{y}")
            tw.attributes("-topmost", True)
            lbl = Label(
                tw, text=self.text,
                background="#FFFBCC", foreground="#222222",
                relief="solid", borderwidth=1,
                font=("Segoe UI", 10), padx=6, pady=3
            )
            lbl.pack()

        def _hide(self):
            if self._tip_wnd:
                self._tip_wnd.destroy()
                self._tip_wnd = None

    def add_hover(btn, tooltip_text=""):
        """Attach a light-up hover colour and an optional tooltip to a Button."""
        btn.bind("<Enter>", lambda e: btn.config(bg=HOVER_BG), add="+")
        btn.bind("<Leave>", lambda e: btn.config(bg=NORMAL_BG), add="+")
        if tooltip_text:
            Tooltip(btn, tooltip_text)
    # ──────────────────────────────────────────────────────────────────────────
     
    

    ressourcesPath = os.path.join(BASE_DIR,"ressources")
    launcherOstPath = os.path.join(ressourcesPath,"LauncherOst.wav")
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(launcherOstPath)
        pygame.mixer.music.play(loops=-1)
    except:
        try:
            winsound.PlaySound(launcherOstPath,winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        except:
            pass
    game_path = config.get("GAME_PATH","")

    if not game_path or game_path == "" or not "BLEACH Rebirth of Souls" in game_path:
        flag = True
        while(flag):
            messagebox.showinfo("Bleach not found","BLEACH_Rebirth_of_Souls.exe not found. You can find it in your steam folder, press ok then select it")
            game_path = filedialog.askopenfilename(title="Select Bleach rebirth of souls",filetypes=[("Executable files", "*.exe")])
            
            if game_path == "":
                exit()
            
            if"BLEACH_Rebirth_of_Souls.exe" in game_path:
                flag = False

        parent_dir = os.path.dirname(game_path)
        game_path = str(parent_dir)
        config["GAME_PATH"] = game_path
        with open(config_path, "w") as f:
            json.dump(config, f)

    def saveJson():
        with open(config_path,"w") as f:
            json.dump(config,f)

    def injectFolder(files,folderName):
            action_src = os.path.join(BASE_DIR,"GameVersions",f"{files}",f'{folderName}')
            action_dst = os.path.join(game_path,f'{folderName}')
            print(f"injectFolder: src={action_src}")
            print(f"injectFolder: dst={action_dst}")
            print(f"injectFolder: src exists={os.path.exists(action_src)}")
            shutil.rmtree(action_dst)
            shutil.copytree(action_src, action_dst)
            print(f"injectFolder: copied successfully")

    def injectPerformanceFiles(folderName,lowspecmodornot):
        shutil.copytree(os.path.join(BASE_DIR,"Files","Spec Mod",f'{folderName}',f'{lowspecmodornot}'),
                        os.path.join(game_path,"00HIGH","Effect","spfx","com"),dirs_exist_ok=True)
        shutil.copytree(os.path.join(BASE_DIR,"Files","Spec Mod",f'{folderName}',f'{lowspecmodornot}'),
                        os.path.join(game_path,"01MIDDLE","Effect","spfx","com"),dirs_exist_ok=True)
    
    def repair():
        messagebox.showinfo("Repair", "Please select the BLEACH_Rebirth_of_Souls.exe file from a clean backup folder of the game (your backup folder, not your main Bros folder)")
        repair_game_path = ""
        parent_dir = ""
        if not repair_game_path or repair_game_path == "" or not "BLEACH Rebirth of Souls" in repair_game_path:
            flag = True
            while(flag):
                repair_game_path = filedialog.askopenfilename(title="Select Bleach rebirth of souls",filetypes=[("Executable files", "*.exe")])

                if repair_game_path == "":
                    messagebox.showinfo("Repair", "You cancelled the repair process.")
                    return
                elif"BLEACH_Rebirth_of_Souls.exe" in repair_game_path:
                    parent_dir = os.path.dirname(repair_game_path)
                    repair_game_path = str(parent_dir)
                    if repair_game_path == config["GAME_PATH"]:
                        messagebox.showerror("Error", "You selected the same folder as your main game folder. Please select a backup folder.")
                    else:
                        flag = False
                else : 
                    messagebox.showerror("Error", "You did not select the correct file. Please select the BLEACH_Rebirth_of_Souls.exe file of your backup folder")
        
       
        messagebox.showinfo("Repair", "Repairing files. Please wait")
        repairPage.tkraise()
        window.update()
        
        repairWaitOstPath = os.path.join(BASE_DIR,"ressources","RepairWaitOst.wav")
        repairEndOstPath = os.path.join(BASE_DIR,"ressources","RepairEndOst.wav")
        try:
            pass
            pygame.mixer.music.stop()
            pygame.mixer.music.load(repairWaitOstPath)
            pygame.mixer.music.play(loops=-1)
        except:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
                winsound.PlaySound(repairWaitOstPath, winsound.SND_ASYNC | winsound.SND_LOOP)
            except:
                pass
        
        try:
            subprocess.run([
                "robocopy", repair_game_path, game_path, "/E", "/XO"
            ], capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            shutil.copytree(repair_game_path, game_path, dirs_exist_ok=True)
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(repairEndOstPath)
            pygame.mixer.music.play(loops=-1)
        except:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
                winsound.PlaySound(repairEndOstPath, winsound.SND_ASYNC)
            except:
                pass
        messagebox.showinfo("Repair", "Files repaired successfully!")
        backToMainMenu()
        launcherOstPath = os.path.join(BASE_DIR,"ressources","LauncherOst.wav")
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(launcherOstPath)
            pygame.mixer.music.play(loops=-1)
        except:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
                winsound.PlaySound(launcherOstPath, winsound.SND_ASYNC | winsound.SND_LOOP)
            except:
                pass

    def launch(gameVersion):
        pull_latest()
        window.destroy()
        try: 
            pygame.mixer.music.stop()
        except:
            pass
        
        #folder injection
        injectFolder(gameVersion,"Script")

        #ost choice
        #ostFolder = ""
            #if config["OST_MOD"] == "ON":
                #ostFolder = "Mod"
            #else : 
                #ostFolder = "Default"
            #ostPath = os.path.join(BASE_DIR,"Files","OST",f"{ostFolder}","bgm.bnk")
            #if os.path.exists(ostPath):
                #shutil.copy(
                    #ostPath,
                    #os.path.join(game_path, "Sound")
                #)

        
        #Performance Mode injection
        shutil.copytree(os.path.join(BASE_DIR,"Files","Spec Mod",'reverse_globe_effect_remover_by_grifo',f'{config["reverse_globe_effect_remover_by_grifo"]}',"high"),
                    os.path.join(game_path,"00HIGH","Effect","spfx","com"),dirs_exist_ok=True)
        
        shutil.copytree(os.path.join(BASE_DIR,"Files","Spec Mod",'reverse_globe_effect_remover_by_grifo',f'{config["reverse_globe_effect_remover_by_grifo"]}',"middle"),
                    os.path.join(game_path,"01MIDDLE","Effect","spfx","com"),dirs_exist_ok=True)
            
        for folder in os.listdir(os.path.join(BASE_DIR,"Files","Spec Mod")):
            injectPerformanceFiles(folder,config[folder])
            

        #gamemode injection
        if gameMode != "DEFAULT":
            print(f"DANS GAMEMODE: {gameMode}")
            srcPath = os.path.join(BASE_DIR,"GameModes",f"{gameMode}","Script")
            dstPath = os.path.join(game_path,"Script")
            print(f"GameMode src: {srcPath}")
            print(f"GameMode dst: {dstPath}")
            print(f"GameMode src exists: {os.path.exists(srcPath)}")
            
            shutil.copytree(srcPath, dstPath, dirs_exist_ok=True)
            print("GameMode injection completed")
            srcPath = os.path.join(BASE_DIR,"GameModes",f"{gameMode}","Script")
            dstPath = os.path.join(game_path,"Script")
            
            shutil.copytree(srcPath, dstPath, dirs_exist_ok=True)

            
        #team battle injection
        if config["TEAM_BATTLE"] == "ON":
            srcPath = os.path.join(BASE_DIR,"GameModes","TeamBattle")
            dstPath = os.path.join(game_path,"Script")   
            shutil.copy(
                os.path.join(srcPath,"CharaStatus.fsv"),
                os.path.join(dstPath,"CharaStatus.fsv"))
            print("copied team files")

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
            open_file("steam://rungameid/1689620")
        except:
            print("Error launching game")
        
        

    def readBalanceChanges():
        webbrowser.open("https://rebalance-of-souls.github.io/reBalanceOfSouls.github.io/")
    
    def readCredits():
        creditsFile = os.path.join(BASE_DIR,"Credits","credits.txt")
        if os.path.exists(creditsFile):
            try:
                open_file(creditsFile)
            except:
                print("Error opening credits.txt")


        saveJson()

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
            
        labelGamePath.config(text=f'Current game path : {game_path}')
        
   
    def gameModesMenu():
        gameModesPage.tkraise()

    

    #box
    container = Frame(window, bg=bgcolor)
    container.pack(expand=YES)
    mainPage = Frame(container,bg=bgcolor)
    settingsPage = Frame(container,bg=bgcolor)
    gameModesPage = Frame(container,bg=bgcolor)
    repairPage = Frame(container,bg=bgcolor)

    titleText = "Bleach Rebirth of Souls community patch launcher"
    subTitleText = "made by Nilsix :3"
    #labels
    labelTitle = Label(mainPage, text=titleText, font=("Arial",30),bg=bgcolor,fg=labelcolor)
    labelSubTitle = Label(mainPage,text=subTitleText,font=("Courrier",20),bg=bgcolor,fg=labelcolor)
    labelTitleSettings = Label(settingsPage, text=titleText, font=("Arial",30),bg=bgcolor,fg=labelcolor)
    labelSubTitleSettings = Label(settingsPage,text=subTitleText,font=("Courrier",20),bg=bgcolor,fg=labelcolor)
    labelTitleGameModes = Label(gameModesPage, text=titleText, font=("Arial",30),bg=bgcolor,fg=labelcolor)
    labelSubTitleGameModes = Label(gameModesPage,text=subTitleText,font=("Courrier",20),bg=bgcolor,fg=labelcolor)
    labelTitleRepair = Label(repairPage, text=titleText, font=("Arial",30),bg=bgcolor,fg=labelcolor)
    labelSubTitleRepair = Label(repairPage,text=subTitleText,font=("Courrier",20),bg=bgcolor,fg=labelcolor)
    labelRepairText = Label(repairPage,text="Repairing Files",font=("Courrier",15),bg=bgcolor,fg=labelcolor)
    labelWarning = Label(mainPage, text="Warning : Please only use the non vanilla features in room matches online, not in casual or ranked matches",font=("Courrier",15),bg=bgcolor,fg=labelcolor)
    labelGamePath = Label(mainPage,text=f'Current game path : {game_path}',font=("Courrier",15),bg=bgcolor,fg=labelcolor)
    brosVersion = StringVar()
    gameVersionsList = []
    gameVersionsPath = os.path.join(BASE_DIR,"GameVersions")
    for folder in os.listdir(gameVersionsPath):
        print(folder)
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
        saveJson()
        mainPage.tkraise()

    def baseOnlyFunc():
        global gameMode
        if gameMode == "BaseOnly":
            gameMode = "DEFAULT"
        else:
            gameMode = "BaseOnly"
        actualiseGameModeButtons()
    
    def teamBattleFunc():
        if not os.path.exists(os.path.join(BASE_DIR,"GameModes","TeamBattle","TokenOpen.txt")):
            config["TEAM_BATTLE"] = "OFF"
            saveJson()
            messagebox.showinfo("Team Battle", "You need to contact a Team Battle host to be able to join a team battle, for that, ping one on the discord using @Team Battle Host")
            return
        config["TEAM_BATTLE"] = "ON" if config["TEAM_BATTLE"] == "OFF" else "OFF"
        saveJson()
        teamBattleButton.config(text=f'Team Battle : (Currently {"ON" if config["TEAM_BATTLE"] == "ON" else "OFF"})')
    
    def instantEvoAndSublimationFunc():
        global gameMode
        if gameMode == "InstantEvoAndSublimation":
            gameMode = "DEFAULT"
        else:
            gameMode = "InstantEvoAndSublimation"
        actualiseGameModeButtons()
    
    def eightKonpakusFunc():
        global gameMode
        if gameMode == "EightKonpakus":
            gameMode = "DEFAULT"
        else:
            gameMode = "EightKonpakus"
        actualiseGameModeButtons()
    
    def actualiseGameModeButtons():
        baseOnlyButton.config(text=f'Base Only : (Currently {"ON" if gameMode == "BaseOnly" else "OFF"})')
        instantEvoAndSublimation.config(text=f'Instant Evo and Sublimation : (Currently {"ON" if gameMode == "InstantEvoAndSublimation" else "OFF"})')
        eightKonpakus.config(text=f'8 Konpakus : (Currently {"ON" if gameMode == "EightKonpakus" else "OFF"})')
    
    def unlockDangaiIchigo():
        result = messagebox.askyesno("Unlock Dangai Ichigo", "Unlocking Dangai Ichigo this way will reset your settings and ranked progress , are you sure you want to continue?")
        theDangaiFiles = os.path.join(BASE_DIR,"ressources","savedata.bin")
        if result:
            appdataPath = os.getenv("APPDATA")
            try:
                saveDataPath = os.path.join(appdataPath,"BLEACH Rebirth of Souls","Savedata")
                for folder in os.listdir(saveDataPath):
                    shutil.copy(theDangaiFiles, os.path.join(saveDataPath, folder))
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
                return
            # Copy the dangai files to the save data path
            #shutil.copy2(theDangaiFiles, saveDataPath)
            messagebox.showinfo("Dangai Ichigo unlocked", "Dangai Ichigo unlocked successfully!")
    
    def refreshLauncher():
        if pull_latest():
            messagebox.showinfo("Refresh", "Launcher refreshed successfully! Restart the launcher to apply any code changes.")
        else:
            messagebox.showerror("Refresh", "Could not refresh. Please check your internet connection and try again.")
    
   
   

    textSize = 18
    paddingYvalue = 10
    #buttons
    launchButton = Button(mainPage,text="Launch the game",font=("Courrier",textSize),bg="white",fg=bgcolor,command=preLauncher)
    joinDiscordButton = Button(mainPage,text="Join our discord :) ",font=("Courrier",textSize),command=lambda : webbrowser.open("https://discord.gg/fSbsZE3qSZ"))
    changeGamePathButton =  Button(mainPage,text=f'Change your game path',font=("Courrier",textSize),bg="white",fg=bgcolor,command=changeGamePath)
    readBalanceChangesButton =  Button(mainPage,text=f'Read balance changes',font=("Courrier",textSize),bg="white",fg=bgcolor,command=readBalanceChanges)
    lowSpecButton =  Button(mainPage,text=f'FPS Booster settings',font=("Courrier",textSize),bg="white",fg=bgcolor,command=performanceSettingsMenu)
    CreditsButton = Button(mainPage,text="Credits",font=("Courrier",textSize),bg="white",fg=bgcolor,command=readCredits)
    gameModesButton = Button(mainPage,text="Game Modes",font=("Courrier",textSize),bg="white",fg=bgcolor,command=gameModesMenu)
    unlockDangaiIchigoButton = Button(mainPage,text="Unlock Dangai Ichigo",font=("Courrier",textSize),bg="white",fg=bgcolor,command=unlockDangaiIchigo)
    repairButton = Button(mainPage,text="Repair files",font=("Courrier",textSize),bg="white",fg=bgcolor,command=repair)
    refreshLauncherButton = Button(mainPage,text="Refresh launcher",font=("Courrier",textSize),bg="white",fg=bgcolor,command=refreshLauncher)



    # Apply hover effects to main-page buttons 
    add_hover(launchButton,          "Launch the game using the version selected in the dropdown above.")
    add_hover(joinDiscordButton,     "Open the community Discord server in your browser.")
    add_hover(changeGamePathButton,  "Change the folder path where your copy of Bleach Rebirth of Souls is installed.")
    add_hover(readBalanceChangesButton, "Open the latest balance-changes notes")
    add_hover(gameModesButton,       "Switch between different game modes (Base only, 8 konpaku, etc...)")
    add_hover(lowSpecButton,         "Toggle per-effect FPS booster settings to improve performance on lower-end PCs.")
    add_hover(repairButton,          "Restore your game files from a clean backup copy of the game.")
    add_hover(CreditsButton,         "View the credits for the mods used in this patch.")
    add_hover(unlockDangaiIchigoButton, "Unlocks Dangai Ichigo")
    add_hover(refreshLauncherButton, "Refresh the launcher to get the latest updates.")

    #pack
    labelTitle.pack()
    labelSubTitle.pack()
    labelWarning.pack(fill=X)
    labelGamePath.pack(fill=X)
    brosVersionList.pack(pady=paddingYvalue,fill=X)
    launchButton.pack()
    joinDiscordButton.pack(pady=paddingYvalue,fill=X)
    changeGamePathButton.pack(pady=paddingYvalue,fill=X)
    readBalanceChangesButton.pack(pady=paddingYvalue,fill=X)
    gameModesButton.pack(pady=paddingYvalue,fill=X)
    #ostSettingsButton.pack(pady=paddingYvalue,fill=X)
    lowSpecButton.pack(pady=paddingYvalue,fill=X)
    repairButton.pack(pady=paddingYvalue,fill=X)
    unlockDangaiIchigoButton.pack(pady=paddingYvalue,fill=X)
    refreshLauncherButton.pack(pady=paddingYvalue,fill=X)
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

    # Apply hover effects to settings-page buttons
    add_hover(awakeningAuraButton,    "Toggle the awakening aura visual effect on/off to save GPU performance.")
    add_hover(breakerGrabButton,      "Toggle the breaker grab screen effect on/off.")
    add_hover(hakugekiButton,         "Toggle the Hakugeki flash effect on/off.")
    add_hover(hitEffectButton,        "Toggle hit impact visual effects on/off.")
    add_hover(reverseGlobeButton,     "Toggle the reverse globe screen effect on/off.")
    add_hover(skillActivationButton,  "Toggle the skill activation flash effect on/off.")
    add_hover(mainMenuButton,         "Return to the main menu.")

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
    instantEvoAndSublimation = Button(
        gameModesPage,
        text=f'Instant Evo and Sublimation : (Currently {"ON" if gameMode == "InstantEvoAndSublimation" else "OFF"})',
        font=("Courrier", textSize),
        bg="white",
        fg=bgcolor,
        command=instantEvoAndSublimationFunc
    )

    eightKonpakus = Button(
        gameModesPage,
        text=f'8 Konpakus : (Currently {"ON" if gameMode == "EightKonpakus" else "OFF"})',
        font=("Courrier", textSize),
        bg="white",
        fg=bgcolor,
        command=eightKonpakusFunc
    )
    teamBattleButton.pack(pady=paddingYvalue, fill=X)
    instantEvoAndSublimation.pack(pady=paddingYvalue, fill=X)
    baseOnlyButton.pack(pady=paddingYvalue, fill=X)
    eightKonpakus.pack(pady=paddingYvalue, fill=X)
    gameModesMenuButton.pack(pady=paddingYvalue, fill=X)

    # Apply hover effects to game-modes-page buttons 
    add_hover(teamBattleButton,        "Toggle Team Battle mode: allows team fights.")
    add_hover(instantEvoAndSublimation,"Toggle Instant Evolution & Sublimation: evolution and sublimation happen immediately.")
    add_hover(baseOnlyButton,          "Toggle Base Only mode: disables evolutions and sublimations entirely. Every character starts with 6 konpaku stocks")
    add_hover(eightKonpakus,           "Toggle 8 Konpakus mode: each player starts with 8 Konpaku stocks (revive characters start with 7).")
    add_hover(gameModesMenuButton,     "Return to the main menu.")

    #repairPage
    labelRepairText = Label(
        repairPage,
        text="Repairing files. Please wait",
        font=("Courrier", 35),
        bg=bgcolor,
        fg=labelcolor
    )

    labelSubtitleRepairText = Label(
        repairPage,
        text="Repairing files. Please wait",
        font=("Courrier", 20),
        bg=bgcolor,
        fg=labelcolor
    )
    

    labelTitleRepair.pack(pady=paddingYvalue)
    labelSubTitleRepair.pack(pady=paddingYvalue)
    labelRepairText.pack(pady=200)

    for page in(mainPage,settingsPage,gameModesPage,repairPage):
        page.grid(row=0,column=0,sticky="nsew")
    mainPage.tkraise()

    window.mainloop()
except Exception as e:
    try :
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)
    except:
        pass
    print(f'Error : {e}')
    input("Please ping the error to Nilsix")