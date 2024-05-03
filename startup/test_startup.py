import unittest
from unittest.mock import MagicMock, mock_open, patch

from startup import startup


class TestSpotifyConfig(unittest.TestCase):
    def setUp(self):
        self.startup = startup()
        
    @patch('os.path.abspath')
    @patch('os.path.dirname')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('builtins.input')
    @patch('logging.info')
    @patch('logging.error')
    def test_create_config_file(self, mock_log_error, mock_log_info, mock_input, mock_exists, mock_open, mock_dirname, mock_abspath):
        mock_abspath.return_value = '/fake/dir/script.py'
        mock_dirname.return_value = '/fake/dir'
        mock_exists.return_value = False
        mock_input.side_effect = ['client_id_xxx', 'secret_xxx', 'uri_xxx']

        self.startup._create_config_file()

        mock_open.assert_called_once_with('/fake/dir/../UniversalQueue/Spotify_Interface/creds.config', 'w')
        handle = mock_open()
        handle.write.assert_any_call('[DEFAULT]\n')
        handle.write.assert_any_call('SPOTIFY_CLIENT_ID = client_id_xxx \n')
        handle.write.assert_any_call('SPOTIFY_CLIENT_SECRET = secret_xxx\n')
        handle.write.assert_any_call('SPOTIFY_REDIRECT_URI = uri_xxx\n')
        handle.write.assert_any_call('DEVICE =')
        mock_log_info.assert_called_with("Config file successfully created")
        
        
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="SPOTIFY_USER_REFRESH=some_token\n")
    @patch('logging.info')
    def test_is_refresh_token_exists(self, mock_logging, mock_open, mock_exists):
        """Test the case where the refresh token exists in the config file."""
        result =  self.startup.is_refresh_token()
        mock_logging.assert_called_with("Refresh token already exists")
        self.assertTrue(result)

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="SOME_OTHER_KEY=some_value\n")
    @patch('logging.info')
    def test_is_refresh_token_not_exists(self, mock_logging, mock_open, mock_exists):
        """Test the case where the refresh token does not exist in the config file."""
        result = self.startup.is_refresh_token()
        self.assertFalse(result)
        mock_logging.assert_not_called()

    @patch('os.path.dirname')
    @patch('logging.info')
    def test_config_file_not_exists(self, mock_logging, mock_path):
        """Test the case where the config file does not exist."""
        mock_path.return_value = '/fake/dir'
        result = self.startup.is_refresh_token()
        self.assertFalse(result)



if __name__ == '__main__':
    unittest.main()