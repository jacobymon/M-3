import install_dependencies  # MUST be the first line to install dependencies
import logging
import os
import platform
import subprocess
import sys
import psutil
import tekore as tk
from server import Server

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path + '/../UniversalQueue/Spotify_Interface')
sys.path.append(path + '/../UniversalQueue')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class startup:
    """
    A class that combines all startup operations, runs Spotify, and sets up Spotify refresh token to authorize Spotify API
    """
    def __init__(self):
        self.OS = self._check_operating_system()
    
    
    def _create_config_file(self):
        """
        Creates a configuration file for Spotify API credentials 
        """
        path = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(path, '../UniversalQueue/Spotify_Interface/creds.config')
        if_config_exist = os.path.exists(filename)
        if if_config_exist:
            logging.info("Config file already exists")
            return
        
        Client_ID = input("Please provide your Spotify Client ID: ")
        Client_Secret = input("Please provide your Spotify Client Secret: ")
        Redirect_URI = input("Please provide your Spotify Redirect URI: ")
        
        try:
            with open(filename, 'w') as file:
                file.write('[DEFAULT]\n')
                file.write(f'SPOTIFY_CLIENT_ID = {Client_ID}\n', )
                file.write(f'SPOTIFY_CLIENT_SECRET = {Client_Secret}\n')
                file.write(f'SPOTIFY_REDIRECT_URI = {Redirect_URI}\n')
                file.write("DEVICE =")
            logging.info("Config file successfully created")
            
        except Exception as e:
            logging.error("An error occurred while creating the config file: %s", str(e))
            exit()


    def is_refresh_token(self):
        """
        Checks if a refresh token exists in the configuration file.
        Returns: (bool) True if refresh token exists, False otherwise
        """
        path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_FILE = os.path.join(path, '../UniversalQueue/Spotify_Interface/creds.config')
        if_config_exist = os.path.exists(CONFIG_FILE)
        if not if_config_exist:
            logging.info("Config file does not exist")
            return False
        
        try:
            with open(CONFIG_FILE, 'r') as file:
                for line in file:
                    if "SPOTIFY_USER_REFRESH" in line:
                        logging.info("Refresh token already exists")
                        return True
        except Exception as e:
            logging.error("An error occurred while reading the config file: %s", str(e))
            return False
        
        logging.info("Refresh token does not exist inside config file")
        return False
            

    def create_refresh_token(self):
        """
        Creates a Spotify user refresh token and updates the configuration file.
        Returns: (bool) True if token created, False otherwise
        """
        path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_FILE = os.path.join(path, '../UniversalQueue/Spotify_Interface/creds.config')
        if_config_exist = os.path.exists(CONFIG_FILE)
        if not if_config_exist:
            self._create_config_file()
            
        try:
            client_id, client_secret, redirect_uri = tk.config_from_file(
                CONFIG_FILE)
            conf = (client_id, client_secret, redirect_uri)
            token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)
            tk.config_to_file(CONFIG_FILE, conf + (token.refresh_token,))
            logging.info("Token successfully created")
            return True
        
        except Exception as e:
            logging.error(
                "An error occurred while creating the referesh token: %s", str(e))
            return False


    def is_account_premium(self):
        """
        returns True if the user's Spotify account is premium, False otherwise
        """
        # the import is inside the function because spotify_interface_class fails if config file was not set-up
        try:
            import spotify_interface_class
            spotify_interface = spotify_interface_class.Spotify_Interface_Class()
            cur_user = spotify_interface.get_current_user_info()
            if cur_user.product == 'premium':
                logging.info("The user account is premium")
                return True
            else:
                logging.error('The user account is not premium')
                return False
        except Exception as e:
            logging.error("An error occurred while checking if the user account is premium: %s", str(e))
            return False


    def _check_operating_system(self):
        """
        Checks the operating system and returns the name of the OS.
        """
        OS = platform.system()
        if OS == 'Darwin':
            logging.info("OS successfully retrieved: %s", "Mac")
            return "Mac"
        elif OS == 'Windows' or OS == 'Linux':
            logging.info("OS successfully retrieved: %s", OS)
            return platform.system()
        else:
            logging.error("OS not supported is found: %s", OS)
            return ""


    def _is_spotify_installed_windows(self):
        """
        Returns True if Spotify is installed on Windows, False otherwise
        """
        try:
            list_of_apps = subprocess.run(
            ["powershell", "-Command", "get-StartApps"],  capture_output=True).stdout.splitlines()
        except Exception as e:
            logging.error("An error occurred while retrieving list of registered apps on Windows: %s", str(e))
            return False
        
        for app in list_of_apps:
            if b"Spotify" in app:
                logging.info("Spotify is installed on Windows")
                return True
        logging.error("Spotify is not installed on Windows")
        return False


    def _is_spotify_installed_linux(self):
        """
        Returns True if Spotify is installed on Linux, False otherwise
        """
        # 'which spotify' returns 1 if the application doesn't exist. And os.system() multiplies the output by 256
        if (os.system('which spotify') != 256):
            logging.info("Spotify is installed on Linux")
            return True
        else:
            logging.error("Spotify is not installed on Linux")
            return False


    def _is_spotify_installed_mac(self):
        """
        Returns True if Spotify is installed on Mac, False otherwise
        """
        try:
            spotify_app = os.popen("ls /Applications | grep Spotify ").read()
        except Exception as e:
            logging.error("An error occurred while retrieving list of registered apps on Mac: %s", str(e))
            return False
            
        if spotify_app == "Spotify.app\n":
            logging.info("Spotify is installed on Mac")
            return True
        else:
            logging.error("Spotify is not installed on Mac")
            return False


    def is_spotify_installed(self):
        """
        Returns True if Spotify is installed regardless of the device OS, False otherwise
        """
        if self.OS == 'Windows':
            return self._is_spotify_installed_windows()
        elif self.OS == 'Linux':
            return self._is_spotify_installed_linux()
        elif self.OS == 'Mac':
            return self._is_spotify_installed_mac()
        else:
            logging.error("OS not supported is found: %s", self.OS)
            exit()
    
    
    def is_spotify_running(self):
        """
        return True if Spotify is running on the user's machine, False otherwise
        """
        # Spotify.exe for windows, spotify for linux, and Spotify for Mac
        try:
            if ("Spotify.exe" in (p.name() for p in psutil.process_iter())
                    or "spotify" in (p.name() for p in psutil.process_iter())
                    or "Spotify" in (p.name() for p in psutil.process_iter())):
                logging.info("Spotify is running")
                return True
        except Exception as e:
            logging.error("An error occurred while retrieving running processes: %s", str(e))
            return False
        
        logging.info("Spotify is not running")
        return False
    
    
    def start_spotify(self):
        """
        Starts Spotify on the user's machine
        """
        if self.OS == 'Windows':
            try:
                import AppOpener  # AppOpener is imported here because it crashs if it was imported on a non-Windows machine
                AppOpener.open("spotify")
                logging.info("Spotify started on Windows")
                return True
            except Exception as e:
                logging.error(
                    "An error occurred while starting Spotify on Windows: %s", str(e))
                return False

        elif self.OS == 'Linux':
            try:
                subprocess.run(["spotify"])
                logging.info("Spotify started on Linux")
                return True
            except Exception as e:
                logging.error(
                    "An error occurred while starting Spotify on Linux: %s", str(e))
                return False
                
        elif self.OS == 'Mac':
            try:
                subprocess.run(["open", "spotify://"])
                logging.info("Spotify started on Mac")
                return True
            except Exception as e:
                logging.error(
                    "An error occurred while starting Spotify on Mac: %s", str(e))
                return False
                
        else:
            logging.error("OS not supported is found: %s", self.OS)
            exit()
        

    def main(self):
        """
        specifies order of operations for the class methods to run
        """
        if not self.is_spotify_installed():
            print("You have to install Spotify on your computer first")
            exit()
        if not self.is_spotify_running():
            self.start_spotify()
        if not self.is_refresh_token():
            if not self.create_refresh_token():
                exit()
        if not self.is_account_premium():
            print("You have to upgrade your Spotify account to premium first")
            exit()
        website_server = Server(self.OS)
        website_server.main()


if __name__ == "__main__":
    s = startup()
    s.main()
