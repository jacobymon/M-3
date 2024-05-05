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
        """Tests create_conig_file method success when config file doesn't exist"""
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
        """Test no config file is created when one already exists."""
        mock_join.return_value = expected_creds
        self.startup._create_config_file()
        mock_log.assert_called_once_with("Config file already exists")
        
        
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('logging.Logger.error')
    @patch('builtins.input')
    def test_create_config_file_exception(self, mock_input, mock_log, mock_exist, mock_file_open):
        """Test method gracefully handles exceptions when creating the config file."""
        mock_exist.return_value = False
        mock_input.side_effect = ['a289-kfajek', 'bafoh2fpouenJaF931DF', 'https://example.com//callback']
        mock_file_open.side_effect = PermissionError("Permission denied")
        with self.assertRaises(SystemExit):
            self.startup._create_config_file()
        mock_log.assert_called_once_with("An error occurred while creating the config file: %s", "Permission denied")
        

    @patch('os.path.join')
    @patch('logging.info')
    def test_is_refresh_token_exists(self, mock_logging, mock_join):
        """Test the case where the refresh token exists in the config file."""
        mock_join.return_value = expected_token
        result =  self.startup.is_refresh_token()
        mock_logging.assert_called_once_with("Refresh token already exists")
        self.assertTrue(result)


    @patch('os.path.dirname')
    @patch('logging.info')
    def test_is_refresh_token_config_file_not_exists(self, mock_logging, mock_path):
        """Test the case where the config file does not exist."""
        mock_path.return_value = '/fake/dir'
        result = self.startup.is_refresh_token()
        self.assertFalse(result)
        mock_logging.assert_called_once_with("Config file does not exist")


    @patch('os.path.join')
    @patch('logging.info')
    def test_is_refresh_token_not_exists(self, mock_logging, mock_join):
        """Test the case where the refresh token does not exist in the config file."""
        mock_join.return_value = expected_creds
        result = self.startup.is_refresh_token()
        self.assertFalse(result)
        mock_logging.assert_called_once_with("Refresh token does not exist inside config file")


    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('logging.Logger.error')
    def test_is_refresh_token_file_read_exception(self, mock_log, mock_exist, mock_file_open):
        """Test method gracefully handles exceptions when reading the config file that has the refresh token."""
        mock_exist.return_value = True
        mock_file_open.side_effect = OSError("File is actually actually str | bytes | None")
        self.startup.is_refresh_token()
        mock_log.assert_called_once_with("An error occurred while reading the config file: %s", "File is actually actually str | bytes | None")


    @patch('os.path.join')
    @patch('tekore.prompt_for_user_token')
    @patch('logging.Logger.info')
    def test_create_refresh_token_success(self, mock_log, mock_prompt_token, mock_join):
        """Test successful refresh token creation when passed a config file."""
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


    @patch('os.path.exists')
    @patch('tekore.prompt_for_user_token')
    @patch('logging.error')
    def test_create_refresh_token_exception(self, mock_log, mock_prompt_token, mock_exists):
        """Test exception handling during refresh token creation."""
        mock_exists.return_value = True
        mock_prompt_token.side_effect = AssertionError("state is inconsistent")
        result = self.startup.create_refresh_token()
        self.assertFalse(result)
        mock_log.assert_called_once_with("An error occurred while creating the referesh token: %s", "state is inconsistent")


    @patch('logging.error')
    @patch('builtins.__import__')
    def test_is_account_preimum_exception_handling(self, mock_import, mock_error):
        """Test that the graceful error handling works if the program was not able to identify whether the account is premium."""
        mock_import.side_effect = ImportError("No module named 'spotify_interface_class'")
        result = self.startup.is_account_premium()
        self.assertFalse(result)
        mock_error.assert_called_once_with("An error occurred while checking if the user account is premium: %s", 
                                           "No module named 'spotify_interface_class'")
        
    @patch('logging.error')
    @patch('subprocess.run')
    def test_is_spotify_installed_mac_exception(self, mock_run, mock_error):
        """Test _is_spotify_installed_mac() gracefully handles the program if it was not able 
        to retrieve list of installed apps"""
        mock_run.side_effect = Exception("\'Application\' is not a item")
        result = self.startup._is_spotify_installed_mac()
        self.assertFalse(result)
        mock_error.assert_called_once_with("An error occurred while retrieving list of registered apps on Mac: %s",
                                           "\'Application\' is not a item")
        
        
    @patch('logging.error')
    @patch('subprocess.run')
    def test_is_spotify_installed_windows_exception(self, mock_run, mock_error):
        """Test _is_spotify_installed_windows() gracefully handles the program if it was not able 
        to retrieve list of installed apps"""
        mock_run.side_effect = Exception("Permission Denied. You can't run get-StartApps")
        result = self.startup._is_spotify_installed_windows()
        self.assertFalse(result)
        mock_error.assert_called_once_with("An error occurred while retrieving list of registered apps on Windows: %s",
                                           "Permission Denied. You can't run get-StartApps")
        
    @patch('logging.error')
    def test_is_spotify_installed_unsupported_OS(self, mock_error):
        """Test is_spotify_installed() gracefully exits the program if it was run on an unsupported OS"""
        self.startup.OS = "Android"
        with self.assertRaises(SystemExit):
            self.startup.is_spotify_installed()
        mock_error.assert_called_once_with("OS not supported is found: %s", "Android")
        
        
    @patch('psutil.process_iter')
    @patch('logging.info')
    @patch('logging.error')
    def test_is_spotify_running_error(self, mock_error, mock_info, mock_process_iter):
        """Test that the graceful error handling works if the program couldn't find whether Spotify is running."""
        mock_process_iter.side_effect = Exception("Unexpected error")
        result = self.startup.is_spotify_running()
        self.assertFalse(result)
        mock_error.assert_called_once_with("An error occurred while retrieving running processes: %s", "Unexpected error")


    @patch('logging.Logger.error')
    @patch('builtins.__import__')
    def test_start_spotify_windows_failure(self, mock_import, mock_log):
        """Test that the error handling works when Spotify fails to start on Windows."""
        mock_import.side_effect = ImportError("No module named 'AppOpener'")
        self.startup.OS = 'Windows'
        self.startup.start_spotify()
        mock_log.assert_called_once_with(
            "An error occurred while starting Spotify on Windows: %s", "No module named 'AppOpener'")
        
        
    @patch('subprocess.run')
    @patch('logging.Logger.error')
    def test_start_spotify_linux_failure(self, mock_log, mock_run):
        """Test that the error handling works when Spotify fails to start on Linux."""
        mock_run.side_effect = Exception("Failed to execute command")
        self.startup.OS = 'Linux'
        self.startup.start_spotify()
        mock_log.assert_called_once_with(
            "An error occurred while starting Spotify on Linux: %s", "Failed to execute command")


    @patch('subprocess.run')
    @patch('logging.Logger.error')
    def test_start_spotify_mac_failure(self, mock_log, mock_run):
        """Test that the error handling works when Spotify fails to start on Mac."""
        mock_run.side_effect = Exception("Spotify not installed")
        self.startup.OS = 'Mac'
        self.startup.start_spotify()
        mock_log.assert_called_once_with(
            "An error occurred while starting Spotify on Mac: %s", "Spotify not installed")


    @patch('logging.Logger.error')
    def test_start_spotify_unsupported_os(self, mock_log):
        """Test that the error handling works for unsupported OS."""
        self.startup.OS = 'Android'
        with self.assertRaises(SystemExit):
            self.startup.start_spotify()
        mock_log.assert_called_once_with(
            "OS not supported is found: %s", 'Android')



if __name__ == '__main__':
    unittest.main()