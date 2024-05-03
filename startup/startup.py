import os

path = os.path.dirname(os.path.abspath(__file__))
requirements_path = path + '/../requirements.txt'
os.system("pip install -r " + requirements_path)
import logging
import platform
import subprocess
import sys
from os.path import exists

import psutil
import tekore as tk
from server import Server

sys.path.append(path + '/../UniversalQueue/Spotify_Interface')
sys.path.append(path + '/../UniversalQueue')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class startup():
    def __init__(self):
        self.OS = self._check_operating_system()
    
    def _create_config_file(self):
        path = os.path.dirname(os.path.abspath(__file__))
        filename = path + '/../UniversalQueue/Spotify_Interface/creds.config'
        if_config_exist = exists(filename)
        if if_config_exist:
            logging.info("Config file already exists")
            return
        Client_ID = input("Please provide your Spotify Client ID: ")
        Client_Secret = input("Please provide your Spotify Client Secret: ")
        Redirect_URI = input("Please provide your Spotify Redirect URI: ")
        try:
            with open(filename, 'w') as file:
                file.write('[DEFAULT]\n')
                file.write(f'SPOTIFY_CLIENT_ID = {Client_ID} \n', )
                file.write(f'SPOTIFY_CLIENT_SECRET = {Client_Secret}\n')
                file.write(
                    f'SPOTIFY_REDIRECT_URI = {Redirect_URI}\n')
                file.write("DEVICE =")
            logging.info("Config file successfully created")
        except Exception as e:
            logging.error(
                "An error occurred while creating the config file: %s", e)
            return


    def is_refresh_token(self):
        path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_FILE = path + '/../UniversalQueue/Spotify_Interface/creds.config'
        if_config_exist = exists(CONFIG_FILE)
        if if_config_exist:
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
        CONFIG_FILE = path + '/../UniversalQueue/Spotify_Interface/creds.config'
        if_config_exist = exists(CONFIG_FILE)
        if not if_config_exist:
            self._create_config_file()
        client_id, client_secret, redirect_uri = tk.config_from_file(
            CONFIG_FILE)
        conf = (client_id, client_secret, redirect_uri)
        token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)
        tk.config_to_file(CONFIG_FILE, conf + (token.refresh_token,))
        logging.info("Token successfully created")
        return True

    def is_account_premium(self):
        # the import is inside the function because spotify_interface_class fails if config file was not set-up
        import spotify_interface_class
        spotify_interface = spotify_interface_class.Spotify_Interface_Class()
        cur_user = spotify_interface.get_current_user_info()
        if cur_user.product == 'premium':
            logging.info("The user account is premium")
            return True
        else:
            logging.error('The user account is not premium')
            return False

    def _check_operating_system(self):
        OS = platform.system()
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
        list_of_apps = subprocess.run(
            ["powershell", "-Command", "get-StartApps"],  capture_output=True).stdout.splitlines()
        for app in list_of_apps:
            if b"Spotify" in app:
                logging.info("Spotify is installed on Windows")
                return True
        logging.error("Spotify is not installed on Windows")
        return False


    def _is_spotify_installed_linux(self):
        # 'which spotify' returns 1 if the application doesn't exist. And os.system() multiplies the output by 256
        if (os.system('which spotify') != 256):
            logging.info("Spotify is installed on Linux")
            return True
        else:
            logging.error("Spotify is not installed on Linux")
            return False


    def _is_spotify_installed_mac(self):
        list_of_apps = subprocess.run("mdfind", "KDMItemKind == \'Application\'", capture_output=True, text=True)
        list_of_apps = list_of_apps.strip()
        if "Spotify.app" in list_of_apps:
            logging.info("Spotify is installed on Mac")
            return True
        else:
            logging.error("Spotify is not installed on Mac")
            return False

    def is_spotify_installed(self):
        if self.OS == 'Windows':
            return self._is_spotify_installed_windows()
        elif self.OS == 'Linux':
            return self._is_spotify_installed_linux()
        elif self.OS == 'Mac':
            return self._is_spotify_installed_mac()
        else:
            logging.error("OS not supported is found: %s", str(self.OS))
            return False
    
    def is_spotify_running(self):
        """Checks if Spotify is running on the user's machine
        return True if Spotify is running, False otherwise"""
        # Spotify.exe for windows, spotify for linux, and Spotify for Mac
        if ("Spotify.exe" in (p.name() for p in psutil.process_iter())
                or "spotify" in (p.name() for p in psutil.process_iter())
                or "Spotify" in (p.name() for p in psutil.process_iter())):
            logging.info("Spotify is running")
            return True
        else:
            logging.error("Spotify is not running")
            return False
    
    def start_spotify(self):
        """ Starts Spotify on the user's machine """
        if self.OS == 'Windows':
            try:
                import AppOpener
                AppOpener.open("spotify")
                logging.info("Spotify started on Windows")
            except Exception as e:
                logging.error(
                    "An error occurred while starting Spotify on Windows: %s", e)

        elif self.OS == 'Linux':
            try:
                subprocess.run(["spotify"])
                logging.info("Spotify started on Linux")
            except Exception as e:
                logging.error(
                    "An error occurred while starting Spotify on Linux: %s", e)
                
        elif self.OS == 'Mac':
            try:
                subprocess.run(["open", "spotify://"])
                logging.info("Spotify started on Mac")
            except Exception as e:
                logging.error(
                    "An error occurred while starting Spotify on Mac: %s", e)
                
        else:
            logging.error("OS not supported is found: %s", str(self.OS))
        return

    def main(self):
        if not self.is_spotify_installed():
            print("You have to install Spotify on your computer first")
            return
        if not self.is_spotify_running():
            self.start_spotify()
        if not self.is_refresh_token():
            if not self.create_refresh_token():
                return
        if not self.is_account_premium():
            print("You have to upgrade your Spotify account to premium first")
            return
        website_server = Server(self.OS)
        website_server.main()


if __name__ == "__main__":
    s = startup()
    s.main()
