import logging
import os
import platform
import subprocess
import sys
from os.path import exists

import psutil
import requests
import tekore as tk
import winapps

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append( path + '/../UniversalQueue/Spotify_Interface')
print(sys.path) 
import spotify_interface_class
from server import Server
from UniversalQueue.Spotify_Interface.spotify_interface_class import \
    Spotify_Interface_Class

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



# TODO test everything on MacOS (checking operating system, Checking installtion, check whether it's running, actually running it, opening browser)
# TODO add docstrings
# TODO implement is_account_preimum(), check_refresh_cookie(), walk_user_authentication(), class main method with logic
# TODO implement _is_spotify_installed_mac()


class startup():
    def __init__(self):
        return
        
    def _create_config_file(self):
        path = os.path.dirname(os.path.abspath(__file__))
        filename = path + '/creds.config'
        if_config_exist = exists(filename)
        if(if_config_exist):
            logging.info("Config file already exists")
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

    
    
    def is_refresh_token(self):
        path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_FILE = path + '/creds.config'
        if_config_exist = exists(CONFIG_FILE)
        if(if_config_exist):
            with open(CONFIG_FILE, 'r') as file:
                for line in file:
                    if "SPOTIFY_USER_REFRESH" in line:
                        logging.info("Refresh token already exists")
                        return True
            return False
        else:
            return False
    
    
    
    def create_refresh_token(self):   
        path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_FILE = path +    '/creds.config'
        if_config_exist = exists(CONFIG_FILE)
        if(if_config_exist):
            self._create_config_file()
        client_id, client_secret, redirect_uri = tk.config_from_file(CONFIG_FILE)
        conf = (client_id, client_secret, redirect_uri)
        token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)
        tk.config_to_file(CONFIG_FILE, conf + (token.refresh_token,))
        logging.info("Token successfully created")
        
        
    
    def is_account_premium(self):
        spotify_interface = spotify_interface_class.Spotify_Interface_Class()
        cur_user = spotify_interface.get_current_user_info()
        if cur_user.product == 'premium':
            logging.info("The user account is premium")
            return True
        else:
            logging.error('The user account is not premium')
            print("You have to upgrade your Spotify account to premium")
            return False

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
    
    
    def main(self):
        if not self.is_refresh_token():
            self.create_refresh_token()
        if not self.is_account_premium():
            print("You have to upgrade your Spotify account to premium first")
            return
        if not self.is_spotify_installed():
            print("You have to install Spotify on your computer first")
            return
        if not self.is_spotify_running():
            self.start_spotify()
        website_server = Server()
        website_server.main()

if __name__ == "__main__":
    s = startup()
    s.main()

    

