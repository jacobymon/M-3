import unittest
from unittest.mock import mock_open, patch

from install_dependencies import install_dependencies


class TestInstallDependencies(unittest.TestCase):
    def test_install_packages_file_not_found(self):
        """Test install_packages when the requirements.txt file does not exist."""
        with patch('os.path.exists', return_value=False), \
            patch('os.path.abspath', return_value='/dummy/path'), \
            patch('logging.Logger.error') as mock_log_error:
            install_dependencies.install_packages()
            requirements_path = '/dummy/../requirements.txt'
            mock_log_error.assert_called_once_with( "requirements.txt not found at %s, cannot install python packages", requirements_path)
            

    def test_install_packages_file_exists_install_success(self):
        """Test install_packages when the requirements.txt file exists and pip install succeeds."""
        with patch('os.path.exists', return_value=True), \
             patch('os.system', return_value=0), \
             patch('logging.Logger.info') as mock_log_info:
            install_dependencies.install_packages()
            mock_log_info.assert_called_once_with("Successfully installed required packages for Python")
            
            
    def test_install_packages_file_exists_install_failure(self):
        """Test install_packages when the requirements.txt file exists but pip install fails."""
        with patch('os.path.exists', return_value=True), \
             patch('os.system', return_value=1), \
             patch('logging.Logger.error') as mock_log_error:
            install_dependencies.install_packages()
            mock_log_error.assert_called_once_with("Failed to install required packages for Python with exit code %d", 1)  


    def test_install_packages_exception_raised(self):
        """Test install_packages handling when an exception is raised during pip install."""
        with patch('os.path.exists', return_value=True), \
             patch('os.system') as mock_system, \
            patch('logging.Logger.error') as mock_log_error:

            # Setup the mock to raise an exception when called
            mock_system.side_effect = Exception("Installation failed due to a network issue")
            install_dependencies.install_packages()
            mock_log_error.assert_called_once_with("Failed to install required packages for Python: %s", "Installation failed due to a network issue")  

            
if __name__ == '__main__':
    unittest.main()
