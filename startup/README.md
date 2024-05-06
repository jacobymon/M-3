### Primary Author: Aser Atawya
### startup.py
- It launches the program and acts as the code entry point.
- Simply run startup.py to start the program.
- Please make sure you meet all the requirments listed [in the README of the main page of the repository](https://github.com/jacobymon/M-3/blob/main/README.md) for a successful launch. 
### test_startup.py
- It has the unit tests for startup.py.
- Simply run test_startup.py to automatically run 18 unit tests.
### server.py
- It has the methods that generate the QR Code image and start the backend and frontend.
### test_server.py
- It has the unit tests for server.py.
- Simply run test_server.py to automatically run 11 unit tests for each of the three supported operating systems (Linux, Mac, and Windows), with a total of 33 tests.
### install_dependencies.py
- This file has only 1 method that installs the python dependencies located in requirements.txt. 
- Note: the following line of code ` import install_dependencies ` MUST be the first line in startup.py. So, avoid using the automatic import sorters in most IDEs to prevent changing the order of the imports.
### install_dependencies_tests.py
- It has 4 unit tests for install_dependencies.py
- Simply run install_dependencies_tests.py to test install_dependencies.py
### test_files
- It has example config files used in unit tests.
