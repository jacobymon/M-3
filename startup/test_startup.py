import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

from startup import startup

dirname = os.path.dirname(__file__)
expected_creds = os.path.join(dirname, 'test_files/expected_creds.config')
expected_token = os.path.join(dirname, 'test_files/expected_token.config')
test_creds_for_token = os.path.join(dirname, 'test_files/test_creds_for_token.config')

class TestSpotifyConfig(unittest.TestCase):
    def setUp(self):
        self.startup = startup()


    @patch('os.path.join')
    @patch('os.path.exists')
    @patch('builtins.input')
    @patch('logging.info')
    def test_create_config_file_success(self, mock_log_info, mock_input, mock_exist, mock_join):
        """Tests create_config_file method success when config file doesn't exist
        Preconditions:
        - The config file does not exist (os.path.exists returns False).
        Expected Results:
        - A new config file is created with the specified user inputs.
        - A log message is generated indicating successful creation.
        Assertion:
        - assert the file contents match expected configuration.
        - assert a log message is generated in format: "Config file successfully created"
        """
        mock_join.return_value = "test_creds.config"
        mock_exist.return_value = False
        mock_input.side_effect = ['a289-kfajek', 'bafoh2fpouenJaF931DF', 'https://example.com//callback']
        self.startup._create_config_file()
        with open ('test_creds.config', 'r') as method_output, open(expected_creds, 'r') as expected_output:
            self.assertEqual(method_output.read(), expected_output.read())
        mock_log_info.assert_called_once_with("Config file successfully created")
    
    
    @patch('os.path.join')
    @patch('logging.info')
    def test_create_config_file_existing(self, mock_log, mock_join):
        """Test no config file is created when one already exists
        Preconditions:
        - The config file already exists 
        Expected Results:
        - No new config file is created.
        - A log message is generated indicating the file already exists.
        Assertion:
        - assert a log message is generated in format: "Config file already exists"
        """
        mock_join.return_value = expected_creds
        self.startup._create_config_file()
        mock_log.assert_called_once_with("Config file already exists")
        
        
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('logging.Logger.error')
    @patch('builtins.input')
    def test_create_config_file_exception(self, mock_input, mock_log, mock_exist, mock_file_open):
        """Test method gracefully handles exceptions when creating the config file
        Preconditions:
        - The config file does not exist, and file creation is attempted.
        - An exception is caught during file creation (PermissionError).
        Expected Results:
        - The method exits with a SystemExit due to a permission error.
        - An error log is generated capturing the exception.
        Assertion:
        - assert the method raises SystemExit.
        - assert an error message is generated with the format:
        ("An error occurred while creating the config file: %s", "Permission denied") for exception caught 
        """
        mock_exist.return_value = False
        mock_input.side_effect = ['a289-kfajek', 'bafoh2fpouenJaF931DF', 'https://example.com//callback']
        mock_file_open.side_effect = PermissionError("Permission denied")
        with self.assertRaises(SystemExit):
            self.startup._create_config_file()
        mock_log.assert_called_once_with("An error occurred while creating the config file: %s", "Permission denied")
        

    @patch('os.path.join')
    @patch('logging.info')
    def test_is_refresh_token_exists(self, mock_logging, mock_join):
        """Test the case that method correctly recognize the refresh token if it exists in the config file
        Preconditions:
        - The path to the token is correct and token exists in the config file.
        Expected Results:
        - The method returns True and a log message is generated confirming the token's presence.
        Assertion:
        - assert the return value is True.
        - assert a log message "Refresh token already exists" is logged once
        """
        mock_join.return_value = expected_token
        result =  self.startup.is_refresh_token()
        mock_logging.assert_called_once_with("Refresh token already exists")
        self.assertTrue(result)


    @patch('os.path.dirname')
    @patch('logging.info')
    def test_is_refresh_token_config_file_not_exists(self, mock_logging, mock_path):
        """Test the case where the config file does not exist
        Preconditions:
        - The directory check for the config file returns a path where the file does not exist.
        Expected Results:
        - The method returns False and a log message is generated stating the file's absence.
        Assertion:
        - assert the return value is False.
        - assert a log message "Config file does not exist" is logged once
        """
        mock_path.return_value = '/fake/dir'
        result = self.startup.is_refresh_token()
        self.assertFalse(result)
        mock_logging.assert_called_once_with("Config file does not exist")


    @patch('os.path.join')
    @patch('logging.info')
    def test_is_refresh_token_not_exists(self, mock_logging, mock_join):
        """Test the case where the refresh token does not exist in the config file
        Preconditions:
        - The path to the config file is correct but the token is not present in the file.
        Expected Results:
        - The method returns False.
        - A log message is generated stating the token's absence.
        Assertion:
        - assert the return value is False.
        - assert a log message "Refresh token does not exist inside config file" is logged once 
        """
        mock_join.return_value = expected_creds
        result = self.startup.is_refresh_token()
        self.assertFalse(result)
        mock_logging.assert_called_once_with("Refresh token does not exist inside config file")


    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('logging.Logger.error')
    def test_is_refresh_token_file_read_exception(self, mock_log, mock_exist, mock_file_open):
        """Test method gracefully handles exceptions when reading the config file that has the refresh token
        Preconditions:
        - The config file exists.
        - An exception (OSError) is caught during the file reading process.
        Expected Results:
        - The method catches the exception without crashing and returns false.
        - An error log is generated detailing the read exception.
        Assertion:
        - assert the method returns false, means it continued execution.
        - assert an error message is logged once in format "An error occurred while reading the config file: %s"
        where %s is the caught OSError string message. 
        """
        mock_exist.return_value = True
        mock_file_open.side_effect = OSError("File is actually actually str | bytes | None")
        result = self.startup.is_refresh_token()
        self.assertFalse(result)
        mock_log.assert_called_once_with("An error occurred while reading the config file: %s", "File is actually actually str | bytes | None")


    @patch('os.path.join')
    @patch('tekore.prompt_for_user_token')
    @patch('logging.Logger.info')
    def test_create_refresh_token_success(self, mock_log, mock_prompt_token, mock_join):
        """Test successful refresh token creation when passed a config file
        Preconditions:
        - Config file is correctly specified and accessible.
        - Mock prompt returns a valid token.
        Expected Results:
        - The refresh token is successfully written to the config file.
        - A log message is generated confirming the token creation.
        Assertion:
        - assert the content of the config file matches the expected token.
        - assert a "Token successfully created" log message is logged once.
        """
        with open (test_creds_for_token, 'w') as test_file, open(expected_creds, 'r') as input:
            test_file.write(input.read())
        
        mock_join.return_value = test_creds_for_token
        mock_token = MagicMock()
        mock_token.refresh_token = "AQAjr9uwnLXtF8jxTzyOkI6QuDoQCNo2MHwdxERTyVEQBb-VnYGXlfnfM"
        mock_prompt_token.return_value = mock_token
        result = self.startup.create_refresh_token()
        self.assertTrue(result)
        mock_log.assert_called_once_with("Token successfully created")
        with open (test_creds_for_token, 'r') as method_output, open(expected_token, 'r') as expected_output:
            self.assertEqual(method_output.read(), expected_output.read())


    @patch('os.path.join')
    @patch('tekore.prompt_for_user_token')
    @patch('logging.error')
    def test_create_refresh_token_exception(self, mock_log, mock_prompt_token, mock_join):
        """Test methods catches exceptions and doesn't crash during refresh token creation
        Preconditions:
        - Config file exists and is accessible.
        - An inconsistency or error occurs during token generation.
        Expected Results:
        - The method handles the inconsistency without crashing but fails to create a token.
        - An error log is generated detailing the issue encountered.
        Assertion:
        - assert the return value is False 
        - assert an error message is logged once in format
        "An error occurred while creating the referesh token: %s" where %s is the exception caught
        """
        with open (test_creds_for_token, 'w') as test_file, open(expected_creds, 'r') as input:
            test_file.write(input.read())
        mock_join.return_value = test_creds_for_token 
        mock_prompt_token.side_effect = AssertionError("state is inconsistent")
        result = self.startup.create_refresh_token()
        self.assertFalse(result)
        mock_log.assert_called_once_with("An error occurred while creating the referesh token: %s", "state is inconsistent")


    @patch('logging.error')
    @patch('builtins.__import__')
    def test_is_account_preimum_exception_handling(self, mock_import, mock_error):
        """Test that the graceful error handling works if the program was not able to identify 
        whether the account is premium
        Preconditions:
        - Importing the backend module that scripts the account informations fails with ImportError.
        Expected Results:
        - The method fails to determine the premium status and handles the error.
        - An error log is generated detailing the import error.
        Assertion:
        - assert the return value is False 
        - assert an error message is logged once with the specific exception detail.
        """
        mock_import.side_effect = ImportError("No module named 'spotify_interface_class'")
        result = self.startup.is_account_premium()
        self.assertFalse(result)
        mock_error.assert_called_once_with("An error occurred while checking if the user account is premium: %s", 
                                           "No module named 'spotify_interface_class'")
        
        
    @patch('logging.error')
    @patch('os.popen')
    def test_is_spotify_installed_mac_exception(self, mock_run, mock_error):
        """Test _is_spotify_installed_mac() gracefully handles the program if it was not able
        to retrieve list of installed apps
        Preconditions:
        - A subprocess command fails to execute, leading to an exception.
        Expected Results:
        - The method handles the exception without crashing, returning False.
        - An error log is generated detailing the exception.
        Assertion:
        - assert the return value is False
        - assert an error message is logged once with the specific exception detail.
        """
        mock_run.side_effect = Exception("Permission Denied")
        result = self.startup._is_spotify_installed_mac()
        self.assertFalse(result)
        mock_error.assert_called_once_with("An error occurred while retrieving list of registered apps on Mac: %s",
                                           "Permission Denied")
        
        
    @patch('logging.error')
    @patch('subprocess.run')
    def test_is_spotify_installed_windows_exception(self, mock_run, mock_error):
        """Test _is_spotify_installed_windows() gracefully handles the program if it was not able 
        to retrieve list of installed apps
        Preconditions:
        - A subprocess command fails due to permission issues, leading to an exception.
        Expected Results:
        - The method handles the exception without crashing, returning False.
        - An error log is generated detailing the exception.
        Assertion:
        - assert the return value is False
        - assert an error message is logged once with the specific exception detail.
        """
        mock_run.side_effect = Exception("Permission Denied. You can't run get-StartApps")
        result = self.startup._is_spotify_installed_windows()
        self.assertFalse(result)
        mock_error.assert_called_once_with("An error occurred while retrieving list of registered apps on Windows: %s",
                                           "Permission Denied. You can't run get-StartApps")
        
    @patch('logging.error')
    def test_is_spotify_installed_unsupported_OS(self, mock_error):
        """Test is_spotify_installed() gracefully exits the program if it was run on an unsupported OS
        Preconditions:
        - The OS is identified as unsupported for the operation (Android).
        Expected Results:
        - The method exits the program due to the unsupported OS condition.
        - An error log is generated stating the OS is not supported.
        Assertion:
        - assert the method raises SystemExit.
        - assert an error message is logged once detailing the unsupported OS.
        """
        self.startup.OS = "Android"
        with self.assertRaises(SystemExit):
            self.startup.is_spotify_installed()
        mock_error.assert_called_once_with("OS not supported is found: %s", "Android")
        
        
    @patch('psutil.process_iter')
    @patch('logging.info')
    @patch('logging.error')
    def test_is_spotify_running_error(self, mock_error, mock_info, mock_process_iter):
        """Test that the method gracefully doesn't crash if it couldn't find whether Spotify is running
        Preconditions:
        - An unexpected error occurs during the retrieval of running processes.
        Expected Results:
        - The method handles the unexpected error gracefully, returning False.
        - An error log is generated detailing the unexpected error.
        Assertion:
        - assert the return value is False
        - assert an error message is logged once detailing the error.
        """
        mock_process_iter.side_effect = Exception("Unexpected error")
        result = self.startup.is_spotify_running()
        self.assertFalse(result)
        mock_error.assert_called_once_with("An error occurred while retrieving running processes: %s", "Unexpected error")


    @patch('logging.Logger.error')
    @patch('builtins.__import__')
    def test_start_spotify_windows_failure(self, mock_import, mock_log):
        """Test the method catches exceptions and doesn't crash if Spotify fails to start on Windows.
        Preconditions:
        - Importing a critical module (e.g., for launching applications) fails with ImportError.
        Expected Results:
        - The method handles the ImportError gracefully, without crashing, and finishes execution, returning false.
        - An error log is generated detailing the failure to start Spotify due to missing module.
        Assertion:
        - assert the method returns False.
        - assert an error log is generated indicating the specific import failure.
        """
        mock_import.side_effect = ImportError("No module named 'AppOpener'")
        self.startup.OS = 'Windows'
        result = self.startup.start_spotify()
        self.assertFalse(result)
        mock_log.assert_called_once_with(
            "An error occurred while starting Spotify on Windows: %s", "No module named 'AppOpener'")
        
        
    @patch('subprocess.run')
    @patch('logging.Logger.error')
    def test_start_spotify_linux_failure(self, mock_log, mock_run):
        """Test the method catches exceptions and doesn't crash if Spotify fails to start on Linux.
        Preconditions:
        - A subprocess command to launch Spotify fails with an execution error.
        Expected Results:
        - The method handles the command failure gracefully, continue to execute until it returns false.
        - An error log is generated detailing the command failure.
        Assertion:
        - assert the method retruns false.
        - assert an error log is generated detailing the failure to execute the command.
        """
        mock_run.side_effect = Exception("Failed to execute command")
        self.startup.OS = 'Linux'
        result = self.startup.start_spotify()
        self.assertFalse(result)
        mock_log.assert_called_once_with(
            "An error occurred while starting Spotify on Linux: %s", "Failed to execute command")


    @patch('subprocess.run')
    @patch('logging.Logger.error')
    def test_start_spotify_mac_failure(self, mock_log, mock_run):
        """Test the method catches exceptions and doesn't crash if Spotify fails to start on Mac.
        Preconditions:
        - A subprocess command to launch Spotify fails with an execution error.
        Expected Results:
        - The method handles the command failure gracefully, continue to execute until it returns false.
        - An error log is generated detailing the command failure.
        Assertion:
        - assert the method retruns false.
        - assert an error log is generated detailing the failure to execute the command.
        """
        mock_run.side_effect = Exception("Spotify not installed")
        self.startup.OS = 'Mac'
        result = self.startup.start_spotify()
        self.assertFalse(result)
        mock_log.assert_called_once_with(
            "An error occurred while starting Spotify on Mac: %s", "Spotify not installed")


    @patch('logging.Logger.error')
    def test_start_spotify_unsupported_os(self, mock_log):
        """Test that the program exits it it was run on unsupported OS
        Preconditions:
        - The operation system is set to an unsupported OS type ('Android').
        Expected Results:
        - The method exits the program due to the unsupported OS condition.
        - An error log is generated stating the OS is unsupported.
        Assertion:
        - assert the method raises SystemExit
        - assert an error message is logged once detailing the unsupported OS.
        """
        self.startup.OS = 'Android'
        with self.assertRaises(SystemExit):
            self.startup.start_spotify()
        mock_log.assert_called_once_with(
            "OS not supported is found: %s", 'Android')



if __name__ == '__main__':
    unittest.main()