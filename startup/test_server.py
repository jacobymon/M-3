import logging
import socket
import unittest
from unittest.mock import MagicMock, patch

import qrcode

from server import Server


def create_test_class(os_name):
    "wrapper function to create a test class for a given operating system"
    class TestServer(unittest.TestCase):
        "A class to test the Server class"
        def setUp(self):
            self.os = os_name
            self.server = Server(os=self.os)
            
            
        @classmethod
        def tearDownClass(cls):
            print(f"Completed test cases for {os_name}")


        @patch('socket.socket')
        @patch('logging.Logger.info')
        def test_get_local_ip_success(self, mock_info, mock_socket):
            """Test get_local_ip when socket connects successfuly"""
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            mock_socket_instance.getsockname.return_value = ['192.168.1.1']
            ip = self.server._get_local_ip()
            self.assertEqual(ip, '192.168.1.1')


        @patch('socket.socket')
        @patch('logging.Logger.error') 
        def test_get_local_ip_failure(self, mock_log_error, mock_socket):
            """ Test get_local_ip gracefully handles when socket throws an exception"""
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            mock_socket_instance.connect.side_effect = socket.error("Failed to connect")
            ip = self.server._get_local_ip()
            self.assertIsNone(ip)
            mock_log_error.assert_called_once_with("Failed to connect or retrieve local IP: %s", "Failed to connect")


        @patch('socket.socket')
        @patch('logging.Logger.error') 
        def test_get_local_ip_socket_creation_failure(self, mock_log_error, mock_socket):
            """Test get_local_ip gracefully handles when socket creation fails"""
            mock_socket.side_effect = socket.error("Socket is Timed Out")
            ip = self.server._get_local_ip()
            self.assertIsNone(ip)
            mock_log_error.assert_called_once_with("Socket creation failed: %s", "Socket is Timed Out")


        @patch('qrcode.QRCode.make_image')
        @patch('os.path.join')
        @patch('os.path.dirname')
        @patch('logging.Logger.info')
        def test_generate_qr_code_success(self, mock_info, mock_dirname, mock_join, mock_make_image):
            """Test generate_qr_code when qrcode.make_image saves a valid image"""
            mock_dirname.return_value = '/fake/dir'
            mock_join.return_value = '/fake/dir/../m3-frontend/src/content/qr-code.png'
            mock_image = MagicMock()
            mock_make_image.return_value = mock_image
            self.server.url = 'http://192.168.1.1:3000'
            self.server.generate_qr_code()
            mock_image.save.assert_called_once_with('/fake/dir/../m3-frontend/src/content/qr-code.png')

        
        @patch('qrcode.QRCode.make_image')
        @patch('logging.Logger.error') 
        @patch('logging.Logger.info')
        def test_generate_qr_code_exception(self, mock_info, mock_log_error, mock_make_image):
            """Test generate_qr_code catching exceptions when qrcode.make_image throws any"""
            mock_make_image.side_effect = Exception("Failed to create QR image")
            self.server.url = 'http://127.0.0.1:3000' 
            self.server.generate_qr_code()
            assert not mock_make_image.save.called
            mock_log_error.assert_called_once_with("An error occurred while creating QR code image: %s", "Failed to create QR image")
            
            
        @patch('os.path.exists')
        @patch('logging.Logger.error')
        @patch('os.path.join')
        def test_react_run_no_package_json(self, mock_join, mock_log_error, mock_exists):
            """Test react_run method gracefully exits when package.json is not found"""
            mock_exists.return_value = False
            mock_join.return_value = '/fake/dir/m3-frontend'
            with self.assertRaises(SystemExit):
                self.server.react_run()
            mock_log_error.assert_called_once_with("package.json not found at %s, cannot run React application", "/fake/dir/m3-frontend")
            
            
        @patch('os.path.exists')
        @patch('server.NPMPackage')
        @patch('os.path.join')
        def test_react_run_success(self, mock_join, mock_npm_package, mock_exists):
            """Test react_run method when installation and startup are successful"""
            mock_exists.return_value = True
            mock_join.return_value = '/fake/dir/m3-frontend'
            pkg_mock = MagicMock()
            mock_npm_package.return_value = pkg_mock
            with self.assertLogs(level='INFO') as log:
                    self.server.react_run()
            if self.os == 'Windows':
                mock_npm_package.assert_called_with('/fake/dir/m3-frontend', shell=True)
            else:
                mock_npm_package.assert_called_with('/fake/dir/m3-frontend')
            pkg_mock.install.assert_called_once()
            self.assertIn("React packages successfully installed",log.output[0])
            pkg_mock.run_script.assert_called_once_with('start')


        @patch('os.path.exists')
        @patch('server.NPMPackage')
        @patch('os.path.join')
        @patch('logging.Logger.error')
        def test_react_run_install_failure_start_success(self,  mock_log_error, mock_join, mock_npm_package, mock_exists):
            """Test react_run method gracefully handles when installation fails but startup is successful"""
            mock_exists.return_value = True
            mock_join.return_value = '/fake/dir/m3-frontend'
            pkg_mock = MagicMock()
            mock_npm_package.return_value = pkg_mock
            pkg_mock.install.side_effect = Exception("Network Error")
            self.server.react_run()
            if self.os == 'Windows':
                mock_npm_package.assert_called_with('/fake/dir/m3-frontend', shell=True)
            else:
                mock_npm_package.assert_called_with('/fake/dir/m3-frontend')
            pkg_mock.install.assert_called_once()
            mock_log_error.assert_called_once_with("Failed to install React packages: %s", "Network Error")
            pkg_mock.run_script.assert_called_once_with('start')


        @patch('os.path.exists')
        @patch('server.NPMPackage')
        @patch('os.path.join')
        @patch('logging.Logger.error')
        def test_react_run_start_failure(self,  mock_log_error, mock_join, mock_npm_package, mock_exists):
            """Test program gracefully exits if frontend start fails"""
            mock_exists.return_value = True
            mock_join.return_value = '/fake/dir/m3-frontend'
            pkg_mock = MagicMock()
            mock_npm_package.return_value = pkg_mock
            pkg_mock.run_script.side_effect = Exception("Craco is not installed")
            with self.assertRaises(SystemExit):
                self.server.react_run()
            if self.os == 'Windows':
                mock_npm_package.assert_called_with('/fake/dir/m3-frontend', shell=True)
            else:
                mock_npm_package.assert_called_with('/fake/dir/m3-frontend')
            pkg_mock.install.assert_called_once()
            pkg_mock.run_script.assert_called_once_with('start')
            mock_log_error.assert_called_once_with("Failed to start React app: %s", "Craco is not installed")


        @patch('logging.Logger.error')
        def test_run_backend(self, mock_log):
            """Tests program gracefully exits if run_backend method fails"""
            with patch('importlib.import_module') as mock_import:
                mock_import.side_effect = ImportError("No module named 'UniversalQueueDesign'")
                with self.assertRaises(SystemExit):
                    self.server.run_backend()
                mock_log.assert_called_with("Failed to start backend: %s", "No module named 'UniversalQueueDesign'")
                
                
    TestServer.__name__ = f"TestServer_{os_name}"
    return TestServer

TestServerLinux = create_test_class('Linux')
TestServerWindows = create_test_class('Windows')
TestServerMac = create_test_class('Mac')

if __name__ == '__main__':
    unittest.main()
