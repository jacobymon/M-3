import logging
import os
import platform
import subprocess
from os.path import exists

#from M-3.Spotify_Interface.spotify_interface import Spotify_Interface
import psutil
import requests
import tekore as tk
import winapps

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



# TODO test everything on MacOS (checking operating system, Checking installtion, check whether it's running, actually running it, opening browser)
# TODO add docstrings
# TODO implement is_account_preimum(), check_refresh_cookie(), walk_user_authentication(), class main method with logic
# TODO implement _is_spotify_installed_mac()


class startup():
    def __init__(self):
        self.cookie = None
        
    def _check_operating_system(self):
        OS =  platform.system() 
        if OS == 'Darwin': 
            logging.info("OS successfully retrieved: %s", "Mac")
            return "Mac"
        elif OS == 'Windows' or OS == 'Linux':
            logging.info("OS successfully retrieved: %s", str(OS))
            return platform.system()
        else:
            logging.error("OS not supported is found: %s", str(OS))
            return ""
        
        
    
        
    def _create_config_file(self):
        path = os.path.dirname(os.path.abspath(__file__))
        filename = path + '\creds.config'
        if_file_exist = exists(filename)
        if(if_file_exist):
            return
        try:
            with open(filename, 'w') as file:
                file.write('[DEFAULT]\n')
                file.write('SPOTIFY_CLIENT_ID = xxx \n')
                file.write('SPOTIFY_CLIENT_SECRET = yyy\n')
                file.write('SPOTIFY_REDIRECT_URI = https://example.com/callback\n')
            logging.info("Config file successfully created")
        except Exception as e:
            logging.error("An error occurred while creating the config file: %s", e)

    
    
    def walk_user_authentication(self):   
        path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_FILE = path + '/creds.config'
                
        client_id, client_secret, redirect_uri = tk.config_from_file(CONFIG_FILE)
        conf = (client_id, client_secret, redirect_uri)

        token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)
        tk.config_to_file(CONFIG_FILE, conf + (token.refresh_token,))
        
    
    
    
    def _is_account_preimum(self):
        return
            
        #import from spotify interaface
        

    def _is_spotify_installed_windows(self):
        list_of_apps = subprocess.run(["powershell", "-Command", "get-StartApps"],  capture_output=True).stdout.splitlines()
        for app in list_of_apps:
            if b"Spotify" in app:
                logging.info("Spotify is installed on Windows")
                return True
        logging.error("Spotify is not installed on Windows")
        print("You have to install Spotify on your computer first")
        return False
    
    
    def _is_spotify_installed_linux(self):
        # 'which spotify' returns 1 if the application doesn't exist. And os.system() multiplies the output by 256 
        if(os.system('which spotify') != 256):
            logging.info("Spotify is installed on Linux")
            return True
        else:
            logging.error("Spotify is not installed on Linux")
            print("You have to install Spotify on your computer first")
            return False
        
    def _is_spotify_installed_mac(self):
        # TODO: implement this function 
        raise NotImplementedError("This function is not implemented yet")
        
    
    
    def is_spotify_installed(self):
        OS = self._check_operating_system()
        if OS == 'Windows':
            return self._is_spotify_installed_windows()
        elif OS == 'Linux':
            return self._is_spotify_installed_linux()
        elif OS == 'Mac':
            return self._is_spotify_installed_mac()
        else:
            logging.error("OS not supported is found: %s", str(OS))
            return False


            
    def is_spotify_running(self):
        # Spotify.exe for windows and spotify for linux 
        if ("Spotify.exe" in (p.name() for p in psutil.process_iter()) 
        or "spotify" in (p.name() for p in psutil.process_iter())):
            logging.info("Spotify is running")
            return True
        else:
            logging.error("Spotify is not running")
            return False
        
    
    def start_spotify(self):
        OS = self._check_operating_system()
        if OS == 'Windows':
            try:
                winapps.run("Spotify.exe")
                logging.info("Spotify started on Windows")
            except Exception as e:
                logging.error("An error occurred while starting Spotify on Windows: %s", e)
            
        elif OS == 'Linux':
            try:
                subprocess.run(["spotify"])
                logging.info("Spotify started on Linux")
            except Exception as e:
                logging.error("An error occurred while starting Spotify on Linux: %s", e)
            
        elif OS == 'Mac':
            try:
                subprocess.run(["open", "spotify://"])
                logging.info("Spotify started on Mac")
            except Exception as e:
                logging.error("An error occurred while starting Spotify on Mac: %s", e)
            
        else:
            logging.error("OS not supported is found: %s", str(OS))
            
        return
        


if __name__ == "__main__":
    s = startup()
    s.walk_user_authentication()
    

