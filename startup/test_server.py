import socket
import unittest
from unittest.mock import MagicMock, patch

import qrcode
from server import Server


class TestServer(unittest.TestCase):
    
    def setUp(self):
        self.server = Server(os='Linux')

    @patch('socket.socket')
    def test_get_local_ip_success(self, mock_socket):
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.getsockname.return_value = ['192.168.1.1']
        ip = self.server._get_local_ip()
        self.assertEqual(ip, '192.168.1.1')


    @patch('socket.socket')
    def test_get_local_ip_failure(self, mock_socket):
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect.side_effect = socket.error("Failed to connect")
        with self.assertLogs(level='ERROR') as log:
            ip = self.server._get_local_ip()
            self.assertIsNone(ip)
            self.assertIn("Failed to connect or retrieve local IP", log.output[0])
    
    
    @patch('socket.socket')
    def test_get_local_ip_socket_creation_failure(self, mock_socket):
        mock_socket.side_effect = socket.error("Socket creation failed")
        with self.assertLogs(level='ERROR') as log:
            ip = self.server._get_local_ip()
        self.assertIsNone(ip)
        self.assertIn('Socket creation failed:', log.output[0])


    @patch('qrcode.QRCode.make_image')
    @patch('os.path.join')
    @patch('os.path.dirname')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_generate_qr_code(self, mock_open, mock_dirname, mock_join, mock_make_image):
        mock_dirname.return_value = '/fake/dir'
        mock_join.return_value = '/fake/dir/../m3-frontend/src/content/qr-code.png'
        mock_image = MagicMock()
        mock_make_image.return_value = mock_image
        self.server.url = 'http://192.168.1.1:3000'
        self.server.generate_qr_code()
        mock_image.save.assert_called_once_with('/fake/dir/../m3-frontend/src/content/qr-code.png')
        
    
    @patch('qrcode.QRCode.make_image')
    def test_generate_qr_code_exception(self, mock_make_image):
        mock_make_image.side_effect = Exception("Failed to create QR image")
        with self.assertLogs(level='ERROR') as log:
            self.server.url = 'http://127.0.0.1:3000' 
            self.server.generate_qr_code()
        self.assertIn('An error occurred:', log.output[0])
        
        
    @patch('threading.Thread.start')
    def test_thread_run_backend(self, mock_start):
        self.server.thread_run_backend()
        mock_start.assert_called_once()

if __name__ == '__main__':
    unittest.main()
