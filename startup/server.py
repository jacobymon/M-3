import logging
import os
import platform
import socket
import sys
import threading
import time
import webbrowser

import qrcode
from flask import Flask
from pynpm import NPMPackage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#TODO make it thread safe and find a way to exit the thread when we terminate the application
#TODO Improve docstrings
#TODO Remove Hello World and integrate with the rest

class Server(object):

    def __init__(self, app = Flask(__name__), **configs):
        self.url = None
        
    def _get_local_ip(self): 
        """
        Retrieves the local IP address of the machine.
        
        Raises:
            socket.error: If there is an error creating the socket or connecting to the remote host.
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
            finally:
                UDP_socket.close()
        except socket.error as e:
            logging.error("Socket creation failed: %s", str(e))
        

    def _check_port_availability(self, port):
        """
        Checks if the specified port is available for use.
        
        Args:
            port (int): The port number to check.
        
        Returns:
            bool: True if the port is available, False otherwise.
        
        Raises:
            socket.error: If there is an error creating the socket or binding to the port.
        """
        try:
            soket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                soket_connection.bind(('0.0.0.0', port))
                logging.info("Port %s is available", port)
                soket_connection.close()
                return True
            except socket.error as e:
                logging.info("Port %s caused the error %s", str(port), str(e))
                return False
        except socket.error as e:
            logging.error("Socket creation failed: %s", str(e))
            
            
        
    def select_available_port(self):
        """
        Selects an available port within the range from 8000 to 8100
            
        Returns:
            int: The first available port found within the specified range.
        
        Raises:
            Exception: If no available port is found within the specified range.
        """
        
        startPort = 8000
        endPort = 8100
        selectedPort = 0
        for port in range(startPort, endPort + 1):
            if self._check_port_availability(port):
                selectedPort = port
                return selectedPort

        if selectedPort == 0:
            raise Exception("No available port found.")

        
        
    """
        Generates a QR code from the provided URL and saves it as an image file.
    """
    def generate_qr_code(self):
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
            img = qr.make_image(fill_color="black", back_color="white")
            current_path = os.path.dirname(__file__)
            full_image_path = os.path.join(current_path, "../m3-frontend/src/content/qr-code.png")
            img.save(full_image_path)
            logging.info("QR code image saved successfully.")

        except Exception as e:
            logging.error("An error occurred: %s", e)
    

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

    def _react_run(self):
        operating_system = self._check_operating_system()
        current_path = os.path.dirname(__file__)
        if operating_system == 'Windows':
            pkg = NPMPackage(os.path.join(current_path, '../m3-frontend/package.json'), shell=True)
        else:
            pkg = NPMPackage(os.path.join(current_path, '../m3-frontend/package.json'))
        pkg.run_script('start')

    
    def threaded_react_run(self, **kwargs):
        thread = threading.Thread(target=self._react_run, kwargs=kwargs)
        thread.start()
        
    
    def open_website(self):
        if webbrowser.open(self.url):
            logging.info("Website opened successfully.")
        else:
            logging.error("Failed to open website.")

    def run_backend(self):
        import UniversalQueueDesign
        
    def thread_run_backend(self):
        backend_thread = threading.Thread(target=self.run_backend, args=())
        backend_thread.start()

    def main(self):
        server = Server()
        port = 3000 # server.select_available_port()
        ip = server._get_local_ip()
        server.url = "http://" + ip + ":" + str(port)
        server.generate_qr_code()
        server.thread_run_backend()
        time.sleep(5)
        server._react_run()
        server.open_website()





if __name__ == "__main__":
    s = Server()
    s.main()
