## Requirements 
To run the program, you need to have Spotify app, python3 (preferably >=3.11), pip, and Node.js installed as well as a premium Spotify account.
- Spotify app can be installed using Microsoft Store on Windows, the official installer on Mac downloaded from [Spotify Website](https://www.spotify.com/de-en/download/mac/), command line prompts on Linux found on [Spotify Website](https://www.spotify.com/de-en/download/linux/)
- Python can be downloaded using Microsoft Store on Windows or by downloading the offical installer from [Python website.](https://www.python.org/downloads/)
- Usually, pip is automatically installed with python, and if not, you can install it using the commands explained [here](https://pip.pypa.io/en/stable/installation/) depending on your operating system.
  - To test the installation of pip, simply write pip or pip3 in terminal/CMD/PowerShell depending on your operating system. If pip or pip3 was recognized as a valid command, then you are all set.
- Node.js can be simply downloaded and installed through the prebuilt installer found on Node.js [official website](https://nodejs.org/en/download/current) depending on your operating system.
  - To test the installation of Node.js, simply write npm in terminal/CMD/PowerShell depending on your operating system. If npm was recognized as a valid command, then you are all set.

## Set-up
To use the program, you have to set up a Spotify Web ApI on [Spotify Developers Site](https://developer.spotify.com/documentation/web-api)
- Log into the [dashboard](https://developer.spotify.com/dashboard) using your Spotify premium account.
- Create an app and select "Web API" for the question asking which APIs are you planning to use. Once you have created your app, you will have access to the app credentials.
    -  These app credentials will be required for API authorization to obtain an access token.
    -  There are 3 main credentials: Client ID, Client secret, and Redirect URI. All of the three can be found by accessing the settings tab of the spotify web app you created. 

## Running the program
- Run startup.py found inside the startup directory. 
- Only the first time you run startup.py:
    - It will install dependent packages, so it will take a few minutes.
    - You will be prompted to enter Client ID, Client secret, and Redirect URI to authorize your account and create an access token. After you enter those 3 credentials, you will be directed into your spotify account to authorize the app to play songs. After you accept the authorization, you will be directed to your Redirect URI, and the URL will have the authorization cookie appended to it. Copy the entire URL and paste it as prompted.
- Then, your default browser will open the Web Application!
- Other members can join by scanning the QR code or copying the URL as long as they are connected to the same network.


