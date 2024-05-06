import socket
import unittest
from unittest.mock import MagicMock, patch

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
            """Test get_local_ip when socket connects successfuly
            Preconditions:
            - socket establishes connection with Google DNS successfully
            Expeceted Results:
            - Method returns the IP address of the device in the local network
            Assertion:
            - Assert the return value of the method is the same as the mocked IP 
            and the correct info message is logged in format:
            ("Local IP successfully retrieved: %s", str(ip))
            """
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            mock_socket_instance.getsockname.return_value = ['192.168.1.1']
            ip = self.server._get_local_ip()
            self.assertEqual(ip, '192.168.1.1')
            mock_info.assert_called_once_with("Local IP successfully retrieved: %s", str(ip))


        @patch('socket.socket')
        @patch('logging.Logger.error') 
        def test_get_local_ip_failure(self, mock_log_error, mock_socket):
            """ Test get_local_ip gracefully handles when socket throws an exception
            Preconditions:
            - socket fails to connect returning "Failed to connect" error
            Expected Results:
            - method returns none and logs an error message capturing the error 
            Assertion:
            - assert function return value is None and an error message is logged capturing 
            socket error in format: ("Failed to connect or retrieve local IP: %s", "Failed to connect")
            """
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            mock_socket_instance.connect.side_effect = socket.error("Failed to connect")
            ip = self.server._get_local_ip()
            self.assertIsNone(ip)
            mock_log_error.assert_called_once_with("Failed to connect or retrieve local IP: %s", 
                                                   "Failed to connect")


        @patch('socket.socket')
        @patch('logging.Logger.error') 
        def test_get_local_ip_socket_creation_failure(self, mock_log_error, mock_socket):
            """Test get_local_ip gracefully handles when socket creation fails
            Preconditions
            - socket creation fails with "Socket is Timed Out" error
            Expected Results:
            - method returns none and logs an error message capturing the error
            Assertion:
            - assert function return value is None and an error message is logged capturing 
            exception e in format: ("Socket creation failed: %s", "Socket is Timed Out")
            """
            mock_socket.side_effect = socket.error("Socket is Timed Out")
            ip = self.server._get_local_ip()
            self.assertIsNone(ip)
            mock_log_error.assert_called_once_with("Socket creation failed: %s", "Socket is Timed Out")


        @patch('qrcode.QRCode.make_image')
        @patch('os.path.join')
        @patch('logging.Logger.info')
        def test_generate_qr_code_success(self, mock_info, mock_join, mock_make_image):
            """Test generate_qr_code when qrcode.make_image saves a valid image
            Preconditions:
            - QRCode.make_image successfully returns a mock image object.
            Expected Results:
            - QR code image is successfully saved.
            - An informational log is generated indicating successful save.
            Assertion:
            - assert the save method is called exactly once with the correct path and that an info log
            is generated in format 'QR code image saved successfully.'
            """
            mock_join.return_value = '/fake/dir/../m3-frontend/src/content/qr-code.png'
            mock_image = MagicMock()
            mock_make_image.return_value = mock_image
            self.server.url = 'http://192.168.1.1:3000'
            self.server.generate_qr_code()
            mock_image.save.assert_called_once_with('/fake/dir/../m3-frontend/src/content/qr-code.png')
            mock_info.assert_called_with('QR code image saved successfully.')

        
        @patch('qrcode.QRCode.make_image')
        @patch('logging.Logger.error') 
        def test_generate_qr_code_exception(self, mock_log_error, mock_make_image):
            """Test generate_qr_code catches exceptions when qrcode.make_image throws any
            Preconditions:
            - QRCode.make_image method is set to raise an IOError indicating disk is full.
            Expected Results:
            - The method does not save the QR code image, catch the exception, and an error log is
            generated capturing the exception.
            Assertion:
            - assert that the save method on the image object is not called and that error log is generated
            in the format: ("An error occurred while creating QR code image: %s", "Disk full") for IOError
            """ 
            mock_make_image.side_effect = IOError("Disk full")
            self.server.url = 'http://127.0.0.1:3000' 
            self.server.generate_qr_code()
            assert not mock_make_image.save.called
            mock_log_error.assert_called_once_with("An error occurred while creating QR code image: %s",
                                                   "Disk full")
            
            
        @patch('os.path.dirname')
        @patch('logging.Logger.error')
        def test_react_run_no_package_json(self, mock_log_error, mock_dirname):
            """Test react_run method gracefully exits when package.json is not found
            Preconditions:
            - an invlaid directory is mocked for react_run()
            Expected Results:
            - The method exits the application
            Assertion:
            - Assert the method raises SystmExit
            - Assert an error message is logged with the format:
            "package.json not found at %s, cannot run React application" where %s is the path 
            """
            mock_dirname.return_value = "fake_dir"
            with self.assertRaises(SystemExit):
                self.server.react_run()
            mock_log_error.assert_called_once_with("package.json not found at %s, cannot run React application",
                                                   "fake_dir\\../m3-frontend/package.json")
            
            
        @patch('os.path.exists')
        @patch('server.NPMPackage')
        @patch('os.path.join')
        def test_react_run_success(self, mock_join, mock_npm_package, mock_exists):
            """Test react_run method success when installation and startup are successful
            Preconditions:
            - os.path.exists returns True indicating package.json is present.
            - NPMPackage is properly initialized and the methods are callable.
            Expected Results:
            - NPM packages are installed successfully.
            - React application starts without errors.
            - Info log indicates successful installation and startup.
            Assertion:
            - assert NPM package methods for install and run_script are called exactly once and 
            log contains specific success messages: "React packages successfully installed"
            """
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
        def test_react_run_install_failure_start_success(self,  mock_log_error, mock_join, 
                                                         mock_npm_package, mock_exists):
            """Test react_run method gracefully handles when installation fails but startup is successful
            Preconditions:
            - os.path.exists returns True, indicating presence of required package.json.
            - Installation throws a Network Error exception, but the start script runs successfully.
            Expected Results:
            - Method attempts to install and then run the start script. It doesn't exit()
            - Logs an error message for installation failure but no exception for startup.
            Assertion:
            - assert the install method catch the exception and run_script is still called.
            - assert an error message is logged for installation failure in format:
            ("Failed to install React packages: %s", "Network Error") catching the network error
            """            
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
            mock_log_error.assert_called_once_with("Failed to install React packages: %s", 
                                                   "Network Error")
            pkg_mock.run_script.assert_called_once_with('start')


        @patch('os.path.exists')
        @patch('server.NPMPackage')
        @patch('os.path.join')
        @patch('logging.Logger.error')
        def test_react_run_start_failure(self,  mock_log_error, mock_join, mock_npm_package, 
                                         mock_exists):
            """Test program gracefully exits if frontend start fails
                Preconditions:
                - NPM package initialization and installation occur without issues.
                - The start script command is invalid or fails.
                Expected Results:
                - Method exits with a SystemExit due to failure in running the start script.
                - Logs an error message indicating failure to start the React app.
                Assertion:
                - assert the method raises SystemExit.
                - assert an error log is generated detailing the failure reason.
                """
            mock_exists.return_value = True
            mock_join.return_value = '/fake/dir/m3-frontend'
            pkg_mock = MagicMock()
            mock_npm_package.return_value = pkg_mock
            pkg_mock.run_script.side_effect = AttributeError("Invalid NPM command.")
            with self.assertRaises(SystemExit):
                self.server.react_run()
            if self.os == 'Windows':
                mock_npm_package.assert_called_with('/fake/dir/m3-frontend', shell=True)
            else:
                mock_npm_package.assert_called_with('/fake/dir/m3-frontend')
            pkg_mock.install.assert_called_once()
            pkg_mock.run_script.assert_called_once_with('start')
            mock_log_error.assert_called_once_with("Failed to start React app: %s",
                                                   "Invalid NPM command.")


        @patch('logging.Logger.error')
        def test_run_backend(self, mock_log):
            """Tests program gracefully exits if run_backend method fails
            Preconditions:
            - Importing the backend module fails with ImportError.
            Expected Results:
            - Method exits with a SystemExit due to the import failure.
            - An error log is generated capturing the import error.
            Assertion:
            - assert the method raises SystemExit.
            - assert an error log is generated with the import error message.
            """
            with patch('builtins.__import__') as mock_import:
                mock_import.side_effect = ImportError("No module named 'UniversalQueueDesign'")
                with self.assertRaises(SystemExit):
                    self.server.run_backend()
                mock_log.assert_called_with("Failed to start backend: %s", 
                                            "No module named 'UniversalQueueDesign'")
        
        
        @patch('logging.Logger.error')
        @patch('threading.Thread')
        def test_thread_run_backend(self, mock_thread, mock_log):
            """Tests program gracefully exits if threaded_run_backend method fails
            Preconditions:
            - threading.Thread is initialized but fails, raising a RuntimeError.
            Expected Results:
            - The method exits()
            - An error log is generated capturing the failure
            Assertion:
            - assert the method raises SystemExit 
            - assert an error log is generated detailing the specific reason for the failure.
            """
            mock_thread.side_effect = RuntimeError("called more than once on the same thread object")
            with self.assertRaises(SystemExit):
                    self.server.thread_run_backend()
            mock_log.assert_called_with("Failed to start backend thread: %s", 
                                        "called more than once on the same thread object")
                
                
    TestServer.__name__ = f"TestServer_{os_name}"
    return TestServer

TestServerLinux = create_test_class('Linux')
TestServerWindows = create_test_class('Windows')
TestServerMac = create_test_class('Mac')

if __name__ == '__main__':
    unittest.main()
