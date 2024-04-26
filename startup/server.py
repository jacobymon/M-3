import logging
import socket
import threading
import webbrowser
import qrcode
from flask import Flask

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#TODO make it thread safe and find a way to exit the thread when we terminate the application
#TODO Improve docstrings
#TODO Remove Hello World and integrate with the rest

class Server(object):

    def __init__(self, app = Flask(__name__), **configs):
        self.flask_app = app
        self.flask_configs(**configs)
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
                logging.info("Port %s is available", selectedPort)
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
            
            logging.info("Saving QR code image to 'qr_code.png'")
            img = qr.make_image(fill_color="black", back_color="white")
            img.save("qr_code.png")
            logging.info("QR code image saved successfully.")

        except Exception as e:
            logging.error("An error occurred: %s", e)
    

    def flask_configs(self, **configs):
        for config, value in configs:
            self.flask_app.config[config.upper()] = value

    def flask_add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=['GET'], *args, **kwargs):
        self.flask_app.add_url_rule(endpoint, endpoint_name, handler, methods=methods, *args, **kwargs)

    def _flask_run(self, **kwargs):
        self.flask_app.run(**kwargs)
        return
        
    def threaded_flask_run(self, **kwargs):
        thread = threading.Thread(target=self._flask_run, kwargs=kwargs)
        thread.start()
        
    
    def open_website(self):
        if webbrowser.open(self.url):
            logging.info("Website opened successfully.")
        else:
            logging.error("Failed to open website.")
        
        
    def hello_world(self):
        """ Dummy Function"""
        return 'Hello World'

    def main(self):
        server = Server()
        port = server.select_available_port()
        ip = server._get_local_ip()
        server.url = "http://" + ip + ":" + str(port)
        server.generate_qr_code()
        server.flask_add_endpoint('/', 'hello_world', self.hello_world)
        server.threaded_flask_run(host = ip, port = port)
        server.open_website()



if __name__ == "__main__":
    s = Server()
    s.main()
