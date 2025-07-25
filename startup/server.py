import logging
import os
import socket
import subprocess
import sys
import threading
import time

import qrcode
from pynpm import NPMPackage

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Server:
    """
    A class to start the backend and frontend of the web application and create QR code image for the frontend.

    Attributes:
        os (str): The device operating system
        url (str): The URL where the web app can be accessed once running.
    """

    def __init__(self, os, **configs):
        self.url = None
        self.os = os
        self.backend_ip = None

    def _get_local_ip(self):
        """
        Retrieves the local IP address of the machine by attempting a connection with Google DNS

        Returns: (str) the device local IP address
        """
        try:
            UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # Use Google's DNS server as destination to expose local IP
                UDP_socket.connect(("8.8.8.8", 80))
                IP = UDP_socket.getsockname()[0]
                logging.info("Local IP successfully retrieved: %s", str(IP))
                return IP
            except socket.error as e:
                logging.error("Failed to connect or retrieve local IP: %s", str(e))
                return None
            finally:
                UDP_socket.close()
        except socket.error as e:
            logging.error("Socket creation failed: %s", str(e))
            return None

    def _update_frontend_config(self):
        """
        Updates the frontend .env file with the backend IP address
        """
        try:
            current_path = os.path.dirname(__file__)
            env_path = os.path.join(current_path, '../m3-frontend/.env')
            
            with open(env_path, 'w') as f:
                f.write(f'REACT_APP_BACKEND_IP="{self.backend_ip}"\n')
            
            logging.info(f"Updated frontend .env file with backend IP: {self.backend_ip}")
        except Exception as e:
            logging.error(f"Failed to update frontend .env file: {e}")

    def generate_qr_code(self):
        """
        Generates a QR code from the provided URL and saves it as an image file.
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.url)
            qr.make(fit=True)

            logging.info("Saving QR code image to 'qr-code.png'")
            qr_code_img = qr.make_image(fill_color="black", back_color="white")
            current_path = os.path.dirname(__file__)
            full_image_path = os.path.join(
                current_path, "../m3-frontend/src/content/qr-code.png")
            qr_code_img.save(full_image_path)
            logging.info("QR code image saved successfully.")

        except Exception as e:
            logging.error("An error occurred while creating QR code image: %s", str(e))

    def react_run(self):
        """
        Runs the frontend React application and installs required packages.
        """
        current_path = os.path.dirname(__file__)
        full_package_json_path = os.path.join(current_path, '../m3-frontend/package.json')
        
        if not os.path.exists(full_package_json_path):
            logging.error("package.json not found at %s, cannot run React application", full_package_json_path)
            exit()
            
        try:
            if self.os == 'Windows':
                pkg = NPMPackage(full_package_json_path, shell=True)
            else:
                pkg = NPMPackage(full_package_json_path)
            pkg.install()  # installs required React packages
            logging.info("React packages successfully installed")
        except Exception as e:
            logging.error("Failed to install React packages: %s", str(e))
            
        try:
            pkg.run_script('start')
        except Exception as e:
            logging.error("Failed to start React app: %s", str(e))
            exit()

    def run_backend(self):
        """
        Runs the backend Flask application 
        """
        try:
            current_path = os.path.dirname(__file__)
            backend_path = os.path.join(current_path, '../UniversalQueue')
            backend_script = os.path.join(backend_path, 'UniversalQueueDesign.py')
            
            logging.info(f"Starting backend at: {backend_script}")
            
            # Add the backend path to Python path
            sys.path.insert(0, backend_path)
            
            # Run the backend script
            result = subprocess.run([sys.executable, backend_script], 
                                  cwd=backend_path, 
                                  capture_output=False)
            
            if result.returncode != 0:
                logging.error(f"Backend exited with code: {result.returncode}")
                
        except Exception as e:
            logging.error("Failed to start backend: %s", str(e))
            exit()

    def thread_run_backend(self):
        """
        Runs the backend application in a separate thread to allow the frontend to run on the main thread
        """
        try:
            backend_thread = threading.Thread(target=self.run_backend, args=())
            backend_thread.daemon = True  # Allow main program to exit
            backend_thread.start() 
            logging.info("Backend thread started successfully")
        except Exception as e:
            logging.error("Failed to start backend thread: %s", str(e))
            exit()
        
    def main(self):
        """
        specifies order of operations for the class methods to run
        """
        port = 3000
        ip = self._get_local_ip()
        
        if ip is None:
            logging.error("Failed to retrieve IP address, using localhost")
            ip = "localhost"
        
        self.backend_ip = ip
        self.url = "http://" + ip + ":" + str(port)
        
        # Update frontend configuration with backend IP
        self._update_frontend_config()
        
        # Generate QR code
        self.generate_qr_code()
        
        # Start backend in separate thread
        self.thread_run_backend()
        
        # Wait for backend to start
        time.sleep(8)  # Increased wait time
        
        # Start frontend
        self.react_run()