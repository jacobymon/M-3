import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class InstallDependencies:
    def __init__(self) -> None:
        pass

    @staticmethod
    def install_packages():
        """
        Installs the required packages for Python from requirements.txt.
        """
        path = os.path.dirname(os.path.abspath(__file__))
        requirements_path = os.path.join(path, '../requirements.txt')

        if not os.path.exists(requirements_path):
            logging.error(
                "requirements.txt not found at %s, cannot install Python packages", requirements_path)
            return

        try:
            # Use subprocess to run pip install for better error handling
            logging.info("Installing packages from %s", requirements_path)
            result = subprocess.run(
                ["pip", "install", "-r", requirements_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode == 0:
                logging.info("Successfully installed required packages for Python")
            else:
                logging.error("Failed to install required packages for Python")
                logging.error("Error: %s", result.stderr)
        except Exception as e:
            logging.error("Failed to install required packages for Python: %s", str(e))


# Run the installation process
InstallDependencies.install_packages()