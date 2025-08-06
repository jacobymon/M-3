## Requirements 
To run the program, you need to have Spotify app, python3 (preferably >=3.11), pip, and Node.js installed as well as a premium Spotify account.
- Spotify app can be installed using Microsoft Store on Windows, the official installer on Mac downloaded from [Spotify Website](https://www.spotify.com/de-en/download/mac/), or command line prompts on Linux found on [Spotify Website](https://www.spotify.com/de-en/download/linux/)
- Python can be downloaded using Microsoft Store on Windows or by downloading the offical installer for Windows, Mac, or Linux from [Python website.](https://www.python.org/downloads/)
- Usually, pip is automatically installed with python, and if not, you can install it using the commands explained [here](https://pip.pypa.io/en/stable/installation/) depending on your operating system.
  - To test the installation of pip, simply write pip or pip3 in terminal/CMD/PowerShell depending on your operating system. If pip or pip3 was recognized as a valid command, then you are all set.
- Node.js can be simply downloaded and installed through the prebuilt installer found on Node.js [official website](https://nodejs.org/en/download/current) depending on your operating system.
  - To test the installation of Node.js, simply write npm in terminal/CMD/PowerShell depending on your operating system. If npm was recognized as a valid command, then you are all set.

## Set-up
This application requires API credentials from both Spotify and YouTube to function properly.

### Spotify Web API Setup
To use Spotify functionality, you need to set up a Spotify Web API on [Spotify Developers Site](https://developer.spotify.com/documentation/web-api)
- Log into the [dashboard](https://developer.spotify.com/dashboard) using your Spotify premium account.
- Create an app and select "Web API" for the question asking which APIs are you planning to use. Once you have created your app, you will have access to the app credentials.
    -  These app credentials will be required for API authorization to obtain an access token.
    -  There are 3 main credentials: Client ID, Client secret, and Redirect URI. All of the three can be found by accessing the settings tab of the spotify web app you created.
    -  **Important:** Set your Redirect URI to `http://localhost:8080/callback` (this exact URL is required for the application to work)

### YouTube Data API Setup  
To use YouTube functionality, you need to set up YouTube Data API v3 access:
- Go to the [Google Cloud Console](https://console.developers.google.com/)
- Create a new project or select an existing one:
  - Click "Select a project" at the top of the page
  - Click "NEW PROJECT" if you don't have one
  - Enter a project name (e.g., "M3-Music-Queue") and click "CREATE"
- Enable the YouTube Data API v3:
  - In the left sidebar, click "APIs & Services" → "Library"
  - Search for "YouTube Data API v3"
  - Click on it and press "ENABLE"
- Create an API Key:
  - Go to "APIs & Services" → "Credentials"
  - Click "CREATE CREDENTIALS" → "API key"
  - Copy the generated API key (you'll need this when running the program)
  - **Optional but recommended:** Click "RESTRICT KEY" to limit it to YouTube Data API v3 only

**Note:** The YouTube API is free for reasonable usage (up to 10,000 quota units per day, which allows for thousands of song searches).
    


## Running the program
- Run startup.py found inside the startup directory using an IDE, such as Visual Studio Code, or through the command line:
  ```
  python startup/startup.py 
  ```
- Only the first time you run startup.py:
    - It will install dependent packages, so it may take a few minutes.
    - You will be prompted to enter Client ID, Client secret, and Redirect URI to authorize your account and create an access token. After you enter those 3 credentials, you will be directed into your spotify account to authorize the app to play songs. After you accept the authorization, you will be directed to your Redirect URI, and the URL will have the authorization cookie appended to it. Copy the entire URL and paste it as prompted.
- Then, your default browser will open the Web Application!
- Other members can join by scanning the QR code or copying the URL as long as they are connected to the same network.

### In case of providing invalid credentials:
If you entered a wrong Client ID, Client Secret, or Redirect URI, the Spotify pop-up webpage that authorizes your account will warn you which credential is invalid, and the program will not be able to authorize your account. To provide the correct credentials, you can either manually edit the config file or delete the config file and run startup.py again.
The path to the config file is 
```
 M^3\UniversalQueue\api_credentials.config
```
