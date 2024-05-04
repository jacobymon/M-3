import logging
import os

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class install_dependencies:
    def __init__(self) -> None:
        pass
    
    def install_packages():
        """
        installs the required packages for Python
        """
        path = os.path.dirname(os.path.abspath(__file__))
        requirements_path = path + '/../requirements.txt'
        if not os.path.exists(requirements_path):
            logging.error(
                "requirements.txt not found at %s, cannot install python packages", requirements_path)
            return
        try:
            os.system("pip install -r " + requirements_path)
            logging.info("Successfully installed required packages for Python")
        except Exception as e:
            logging.error("Failed to install required packages for Python: %s", e)

install_dependencies.install_packages()