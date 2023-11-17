from sscma_micro.client import Client
from unittest.mock import MagicMock
import unittest


class TestTransport(unittest.TestCase):
    def setUp(self):
        self._client = Client(MagicMock(), timeout=0.1, try_count=1)

    def test_send_command(self):
        # Test sending a command and receiving a response
        self._client._send_handler = MagicMock()
        self._client._send_handler.side_effect = lambda _: self._client.recieve_handler(
            b'\r{"type": 0, "name": "TEST", "data": "test_response"}\n')
        response = self._client.send_command("AT+TEST")
        self.assertEqual(response["name"], "TEST")
        self.assertEqual(response["data"], "test_response")

        # Test sending a command and not receiving a response
        self._client._send_handler = MagicMock()
        self._client._send_handler.side_effect = lambda _: None
        response = self._client.send_command("AT+test_command")
        self.assertIsNone(response)
        

if __name__ == '__main__':
    unittest.main()
