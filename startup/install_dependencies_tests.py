import unittest
from unittest.mock import mock_open, patch

from install_dependencies import install_dependencies


class TestInstallDependencies(unittest.TestCase):
    def test_install_packages_file_not_found(self):
        """Test install_packages when the requirements.txt file does not exist.
        Preconditions:
        - requirements.txt does not exist
        Expected Results:
        - method should gracefully handle when requirements.txt does not exist by logging the error and returning
        Assertion
        - Assert method returns none 
        - Assert one error message is logged in format:
        ("requirements.txt not found at %s, cannot install python packages", requirements_path)

        """
        with patch('os.path.abspath', return_value='/dummy/path'), \
            patch('logging.Logger.error') as mock_log_error:
            result = install_dependencies.install_packages()
            self.assertIsNone(result)
            requirements_path = '/dummy/../requirements.txt'
            mock_log_error.assert_called_once_with( "requirements.txt not found at %s, cannot install python packages", 
                                                   requirements_path)
            

    def test_install_packages_file_exists_install_success(self):
        """Test install_packages when the requirements.txt file exists and pip install succeeds.
        Preconditions:
        - requirements.txt exists and has valid packages to install
        Expected Results:
        - method should install dependencies without any exceptions called
        Assertion:
        - Assert that exit-code = 0
        - Asser the method logs the correct message "Successfully installed required packages for Python"
        """
        with patch('os.path.exists', return_value=True), \
             patch('os.system', return_value=0), \
             patch('logging.Logger.info') as mock_log_info:
            result = install_dependencies.install_packages()
            assert result == 0
            mock_log_info.assert_called_once_with("Successfully installed required packages for Python")
            
            
    def test_install_packages_file_exists_install_failure(self):
        """Test install_packages gracefully handles when the requirements.txt file exists but pip install fails.
        Preconditions:
        - requirements.txt exists and has valid packages to install
        Expected Results:
        - method should gracefully handle when pip install fails by logging the error and returning
        Assertion:
        - Assert that exit-code = 1,
        - Assert 1 correct error message is logged in format:
        ("Failed to install required packages for Python with exit code %d", exit_code)
        """
        with patch('os.path.exists', return_value=True), \
             patch('os.system', return_value=1), \
             patch('logging.Logger.error') as mock_log_error:
            result = install_dependencies.install_packages()
            assert result == 1
            mock_log_error.assert_called_once_with("Failed to install required packages for Python with exit code %d", 1)


    def test_install_packages_exception_caught(self):
        """Test install_packages handling when an exception is caught during pip install.
        Preconditions:
        - requirements.txt exists and has valid packages to install
        Expected Results:
        - method should gracefully handle when an exception is caught by logging the error
        Assertion:
        - Assert method return None
        - Assert correct error message logged in format:
        ("Failed to install required packages for Python: %s", str(e)) for exception e caught
        """
        with patch('os.path.exists', return_value=True), \
             patch('os.system') as mock_system, \
            patch('logging.Logger.error') as mock_log_error:

            # Setup the mock to catch an exception when calling pip
            mock_system.side_effect = Exception("Installation failed due to a network issue")
            result = install_dependencies.install_packages()
            self.assertIsNone(result)
            mock_log_error.assert_called_once_with("Failed to install required packages for Python: %s",
                                                   "Installation failed due to a network issue")  

            
if __name__ == '__main__':
    unittest.main()
