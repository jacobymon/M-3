import install_dependencies  
import logging
import os
import platform
import subprocess
import sys
import psutil
import tekore as tk
import requests
from server import Server

# FOR WINDOWS SUPPORT
if platform.system() == "Windows":
    import winreg

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
    
    def _check_operating_system(self):
        """
        Checks the operating system and returns the OS type
        
        Returns: (str) Operating system type ('Windows', 'Darwin', 'Linux')
        """
        os_type = platform.system()
        logging.info(f"Detected operating system: {os_type}")
        return os_type
    
    def _create_config_file(self):
        """
        Creates a configuration file for Spotify and YouTube API credentials 
        """
        path = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(path, '../UniversalQueue/api_credentials.config')  # CONFIRM: New path
        if_config_exist = os.path.exists(filename)
        if if_config_exist:
            logging.info("API credentials config file already exists")
            return
        
        print("\n=== API Setup Required ===")
        print("This app requires both Spotify and YouTube API credentials.")
        print("\nFor Spotify API setup, visit: https://developer.spotify.com/dashboard")
        print("For YouTube API setup, visit: https://console.developers.google.com/")
        print("Create a project and enable YouTube Data API v3\n")
        
        Client_ID = input("Please provide your Spotify Client ID: ")
        Client_Secret = input("Please provide your Spotify Client Secret: ")
        Redirect_URI = input("Please provide your Spotify Redirect URI (default: http://localhost:8080/callback): ") or "http://localhost:8080/callback"
        YouTube_API_Key = input("Please provide your YouTube Data API v3 Key: ")
        
        try:
            with open(filename, 'w') as file:
                file.write('[DEFAULT]\n')
                file.write(f'SPOTIFY_CLIENT_ID = {Client_ID}\n')
                file.write(f'SPOTIFY_CLIENT_SECRET = {Client_Secret}\n')
                file.write(f'SPOTIFY_REDIRECT_URI = {Redirect_URI}\n')
                file.write(f'YOUTUBE_API_KEY = {YouTube_API_Key}\n')
                file.write("DEVICE =\n")  # Keep for compatibility
            logging.info("API credentials config file successfully created")
            
        except Exception as e:
            logging.error("An error occurred while creating the config file: %s", str(e))
            exit()

    
    def is_refresh_token(self):
        """
        Checks if a refresh token exists in the configuration file.
        Returns: (bool) True if refresh token exists, False otherwise
        """
        path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_FILE = os.path.join(path, '../UniversalQueue/api_credentials.config')  # CHANGED: New filename
        if_config_exist = os.path.exists(CONFIG_FILE)
        if not if_config_exist:
            logging.info("API credentials config file does not exist")
            return False
        
        try:
            with open(CONFIG_FILE, 'r') as file:
                for line in file:
                    if "SPOTIFY_USER_REFRESH" in line and "=" in line:
                        refresh_token = line.split("=", 1)[1].strip()
                        if refresh_token and refresh_token != "":
                            logging.info("Refresh token already exists")
                            return True
        except Exception as e:
            logging.error("An error occurred while reading the config file: %s", str(e))
            return False
        
        logging.info("Refresh token does not exist inside config file")
        return False

    def is_youtube_api_key(self):
        """
        Checks if a YouTube API key exists in the configuration file.
        Returns: (bool) True if API key exists, False otherwise
        """
        path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_FILE = os.path.join(path, '../UniversalQueue/api_credentials.config')  # CHANGED: New filename
        if_config_exist = os.path.exists(CONFIG_FILE)
        if not if_config_exist:
            logging.info("API credentials config file does not exist")
            return False
        
        try:
            with open(CONFIG_FILE, 'r') as file:
                for line in file:
                    if "YOUTUBE_API_KEY" in line and "=" in line:
                        api_key = line.split("=", 1)[1].strip()
                        if api_key and api_key != "":
                            logging.info("YouTube API key exists")
                            return True
        except Exception as e:
            logging.error("An error occurred while reading the config file: %s", str(e))
            return False
        
        logging.info("YouTube API key does not exist in config file")
        return False

    def create_refresh_token(self):
        """
        Creates a Spotify user refresh token and updates the configuration file.
        Returns: (bool) True if token created, False otherwise
        """
        path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_FILE = os.path.join(path, '../UniversalQueue/api_credentials.config')  # CHANGED: New filename
        if_config_exist = os.path.exists(CONFIG_FILE)
        if not if_config_exist:
            self._create_config_file()
            
        try:
            client_id, client_secret, redirect_uri = tk.config_from_file(
                CONFIG_FILE)
            conf = (client_id, client_secret, redirect_uri)
            token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)
            tk.config_to_file(CONFIG_FILE, conf + (token.refresh_token,))
            logging.info("Spotify refresh token successfully created")
            return True
        
        except Exception as e:
            logging.error(
                "An error occurred while creating the refresh token: %s", str(e))
            return False
    
    def is_spotify_installed(self):
        """
        Checks if Spotify is installed on the system
        
        Returns: (bool) True if Spotify is installed, False otherwise
        """
        try:
            if self.OS == "Windows":
                # Check for Spotify in common Windows locations
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Spotify")
                    winreg.CloseKey(key)
                    return True
                except WindowsError:
                    return False
            elif self.OS == "Darwin":  # macOS
                # Check if Spotify app exists
                spotify_path = "/Applications/Spotify.app"
                return os.path.exists(spotify_path)
            elif self.OS == "Linux":
                # Check if spotify command exists
                result = subprocess.run(['which', 'spotify'], 
                                    capture_output=True, text=True)
                return result.returncode == 0
            else:
                logging.warning(f"Unknown operating system: {self.OS}")
                return False
        except Exception as e:
            logging.error(f"Error checking Spotify installation: {e}")
            return False

    def is_spotify_running(self):
        """
        Checks if Spotify is currently running
        
        Returns: (bool) True if Spotify is running, False otherwise
        """
        try:
            for process in psutil.process_iter(['pid', 'name']):
                if 'spotify' in process.info['name'].lower():
                    logging.info("Spotify is already running")
                    return True
            logging.info("Spotify is not running")
            return False
        except Exception as e:
            logging.error(f"Error checking if Spotify is running: {e}")
            return False

    def start_spotify(self):
        """
        Starts Spotify application based on the operating system
        """
        try:
            logging.info("Starting Spotify...")
            
            if self.OS == "Windows":
                # Try to start Spotify on Windows
                subprocess.Popen(['spotify'], shell=True)
            elif self.OS == "Darwin":  # macOS
                # Start Spotify on macOS
                subprocess.Popen(['open', '-a', 'Spotify'])
            elif self.OS == "Linux":
                # Start Spotify on Linux
                subprocess.Popen(['spotify'])
            else:
                logging.warning(f"Unknown operating system: {self.OS}")
                print("Please start Spotify manually")
                return
            
            # Wait a moment for Spotify to start
            import time
            time.sleep(3)
            
            # Verify it started
            if self.is_spotify_running():
                logging.info("Spotify started successfully")
            else:
                logging.warning("Spotify may not have started properly")
                print("Please ensure Spotify is running before continuing")
                
        except Exception as e:
            logging.error(f"Error starting Spotify: {e}")
            print("Could not start Spotify automatically. Please start it manually.")

    def is_account_premium(self):
        """
        Checks if the Spotify account is premium by testing playback capabilities
        
        Returns: (bool) True if account is premium, False otherwise
        """
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            CONFIG_FILE = os.path.join(path, '../UniversalQueue/api_credentials.config')
            
            if not os.path.exists(CONFIG_FILE):
                logging.error("Config file does not exist")
                return False
            
            # Read config file and check for required credentials
            config_data = {}
            with open(CONFIG_FILE, 'r') as file:
                for line in file:
                    if "=" in line and not line.strip().startswith('['):
                        key, value = line.split("=", 1)
                        config_data[key.strip()] = value.strip()
            
            client_id = config_data.get('SPOTIFY_CLIENT_ID')
            client_secret = config_data.get('SPOTIFY_CLIENT_SECRET')
            refresh_token = config_data.get('SPOTIFY_USER_REFRESH')
            
            # Check if we have all required credentials
            if not all([client_id, client_secret]):
                logging.error("Missing Spotify client credentials")
                return False
                
            if not refresh_token:
                logging.warning("No refresh token found - cannot check premium status yet")
                return True  # Assume premium for now, will be checked later
            
            # Use tekore to check premium status
            token = tk.refresh_user_token(client_id, client_secret, refresh_token)
            spotify = tk.Spotify(token)
            
            # Get current user info
            user = spotify.current_user()
            
            if hasattr(user, 'product') and user.product == 'premium':
                logging.info("Premium account detected")
                return True
            else:
                logging.info("Free account detected - premium required")
                return False
                
        except Exception as e:
            logging.error(f"Error checking premium status: {e}")
            # If we can't check, assume it's premium and let the app handle errors later
            return True

    def main(self):
        """
        specifies order of operations for the class methods to run
        """
        if not self.is_spotify_installed():
            print("You have to install Spotify on your computer first")
            exit()
        if not self.is_spotify_running():
            self.start_spotify()
        if not self.is_refresh_token() or not self.is_youtube_api_key():
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
