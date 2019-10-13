import asyncio
import subprocess
import sys
import json, urllib.request, os, os.path
import user_config, corrections
import datetime
from galaxy.api.consts import LicenseType, LocalGameState, Platform
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, Game, LicenseInfo, LocalGame, GameTime

class RetroarchPSXPlugin(Plugin):

    def __init__(self, reader, writer, token):
        super().__init__(Platform.PlayStation, "0.2", reader, writer, token)
        self.game_cache = []
        self.playlist_path = user_config.emu_path + "playlists/Sony - Playstation.lpl"
        self.proc = None
        self.game_run = ""
        with open(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/PS1_archive.json"), errors= "ignore") as serials_json:
            self.serials = json.load(serials_json)

   
    async def authenticate(self, stored_credentials=None):
        creds = {}
        creds["user"] = "RAUser"
        self.store_credentials(creds)
        return Authentication("RAUser", "Retroarch")
    
    async def pass_login_credentials(self, step, credentials, cookies):
        creds = {}
        creds["user"] = "RAUser"
        self.store_credentials(creds)
        return Authentication("RAUser", "Retroarch")    
    
    async def get_owned_games(self):
        self.update_game_cache()   
        
        return self.game_cache  
    
    #Scans retroarch playlist for roms in rom_path and adds them to self.game_cache
    def update_game_cache(self):   
        game_list = []
        region = ""
        serial = ""
    
        if os.path.isfile(self.playlist_path):
            with open(self.playlist_path) as playlist_json:
                playlist_dict = json.load(playlist_json)
            for entry in playlist_dict["items"]:                
                if os.path.abspath(user_config.rom_path) in os.path.abspath(entry["path"]) and os.path.isfile(entry["path"]):
                    if "(Europe)" in entry["label"]:
                        region = "PAL"
                    if "(USA)" in entry["label"]:
                        region = "NTSC-U"
                    if "(Japan)" in entry["label"]:
                        region = "NTSC-J"
                    if entry["label"] in corrections.correction_list:
                        correct_name = corrections.correction_list[entry["label"].split(" (")[0]]
                    else:
                        correct_name = entry["label"].split(" (")[0]
                    for s_entry in self.serials:
                        if entry["label"].split(" (")[0].upper() == s_entry["NAME"].split(" - [")[0] and region == s_entry["REGION"]:                        
                            serial = s_entry["SERIAL"].replace("-","")
                    if "Disc" in entry["label"] and entry["label"] not in corrections.correction_list:
                        if "Disc 1" in entry["label"]:
                            pass
                        else:
                            continue
                    
                    game_list.append(
                        Game(                          
                            serial,
                            correct_name,
                            None,
                            LicenseInfo(LicenseType.SinglePurchase, None)
                            )
                        )    
                        
        for entry in game_list:
            if entry not in self.game_cache:
                self.game_cache.append(entry)
                self.add_game(entry)
        
        for entry in self.game_cache:
            if entry not in game_list:
                self.game_cache.remove(entry)    
                self.remove_game(entry.game_id)

                    
    #runs update_game_cache in case it is started before get_owned_games. If it runs after it, it just returns self.game_cache with each game as installed
    async def get_local_games(self):
        if not self.game_cache:
            self.update_game_cache()
        local_game_list = []
        for game_entry in self.game_cache:
            local_game_list.append(LocalGame(game_entry.game_id, 1))
        return local_game_list
          
    # Only as placeholders so the launch game feature is recognized
    async def install_game(self, game_id):
        pass

    async def uninstall_game(self, game_id):
        pass
            
    def shutdown(self):
        pass
                      

    #potentially give user more customization possibilities like starting in fullscreen etc 
    async def launch_game(self, game_id): 
        
        if os.path.isfile(self.playlist_path):
            with open(self.playlist_path) as playlist_json:
                playlist_dict = json.load(playlist_json)
        for entry in playlist_dict["items"]:
            if game_id == entry["label"]:
                self.update_local_game_status(LocalGame(game_id, 2))
                self.game_run = entry["label"]
                if user_config.core == 1:
                    self.proc = subprocess.Popen(os.path.abspath(user_config.emu_path + "retroarch.exe" + " -L \"" + user_config.emu_path + "cores/pcsx_rearmed_libretro.dll\" \"" + entry["path"]))
                if user_config.core == 2:
                    self.proc = subprocess.Popen(os.path.abspath(user_config.emu_path + "retroarch.exe" + " -L \"" + user_config.emu_path + "cores/mednafen_psx_libretro\" \"" + entry["path"]))
                if user_config.core == 3:
                    self.proc = subprocess.Popen(os.path.abspath(user_config.emu_path + "retroarch.exe" + " -L \"" + user_config.emu_path + "cores/mednafen_psx_hw_libretro.dll\" \"" + entry["path"]))
                break          
    
    #imports retroarch playtime if existent. For this to work, activate "Save runtime log (aggregate)" in RetroArch settings -> Savings
    async def get_game_time(self, game_id: str, context:any):   

        file_path = ""
        time = 0
        last_played = None
        game_label = ""
        
        for s_entry in self.serials:
            if game_id == s_entry["SERIAL"].replace("-",""):
               game_label = s_entry["NAME"]

        if os.path.isfile(self.playlist_path):
            with open(self.playlist_path) as playlist_json:
                playlist_dict = json.load(playlist_json)
            for rom in playlist_dict["items"]:
                if game_label.split("  -  [")[0] == rom["label"].upper().split(" (")[0]:
                    file_path = user_config.emu_path + "/playlists/logs/" + os.path.abspath(rom["path"]).split(os.path.abspath(user_config.rom_path) + "\\")[1][:-4] + ".lrtl"       
                    if os.path.isfile(file_path):
                        with open(file_path) as json_data:
                            time_data = json.load(json_data)
                        last_played = datetime.datetime.timestamp(datetime.datetime.strptime(time_data["last_played"],'%Y-%m-%d %H:%M:%S'))
                        min_data = datetime.datetime.strptime(time_data["runtime"], '%H:%M:%S')
                        time = min_data.hour*60 + min_data.minute
        return GameTime(game_id, time, last_played)
    
    def tick(self):
        try:
            if self.proc.poll() is not None:
                self.update_local_game_status(LocalGame(self.game_run, 1))
                self.update_game_time(self.get_game_time(self.game_run,None))
                self.proc = None
        except AttributeError:
            pass
            
        self.update_game_cache()    
        self.get_local_games()
        

def main():
    create_and_run_plugin(RetroarchPSXPlugin, sys.argv)
    
if __name__ == "__main__":
    main()      
    
