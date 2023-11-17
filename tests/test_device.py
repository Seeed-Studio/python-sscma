import unittest
import json
from unittest.mock import MagicMock
from sscma_micro.client import Client
from sscma_micro.device import Device, DeviceInfoUnavailableException, PayloadDecodeException


class TestDevice(unittest.TestCase):

    def setUp(self):
        self._client = Client(MagicMock(), timeout=0.1, try_count=1)
        self._device = Device(client=self._client)

    def test_model_fetch_success(self):
        # Mock the query response
        self._client._send_handler = MagicMock()
        self._client._send_handler.side_effect = lambda _: self._client.recieve_handler(
            b'\r{"type": 0, "name": "INFO?", "code": 0, "data": {"crc16_maxim": 51978, "info": "eyJ1dWlkIjoiMHg4MDAxIiwibmFtZSI6IkZhY2UgRGV0ZWN0aW9uIiwidmVyc2lvbiI6IjEuMC4wIiwiY2F0ZWdvcnkiOiJPYmplY3QgRGV0ZWN0aW9uIiwibW9kZWxfdHlwZSI6IlRGTGl0ZSIsImFsZ29yaXRobSI6IllPTE8iLCJkZXNjcmlwdGlvbiI6IlRoaXMgbW9kZWwgaXMgZm9yIGZhY2UgZGV0ZWN0aW9uLiIsImltYWdlIjoiaHR0cHM6Ly9maWxlcy5zZWVlZHN0dWRpby5jb20vc3NjbWEvc3RhdGljL2RldGVjdGlvbl9mYWNlLnBuZyIsImNsYXNzZXMiOlsiRmFjZSJdLCJjb25maWciOnsiY29uZmlkZW5jZV90aHJlc2hvbGQiOjAuNSwiaW91X3RocmVzaG9sZCI6MC40NX0sImRldmljZXMiOlsieGlhb19lc3AzMnMzIl0sInVybCI6Imh0dHBzOi8vZmlsZXMuc2VlZWRzdHVkaW8uY29tL3NzY21hL21vZGVsX3pvby9kZXRlY3Rpb24vbW9kZWxzL3lvbG92NS9GYWNlL3lvbG92NV90aW55X2ZhY2UudGZsaXRlIiwiY2hlY2tzdW0iOiJTSEEtMTpiMmI4NjhjZDYyM2ZmNzU2YTNmYjQ2NjZhYjNmYTMxNjA5YzYzMzRlIiwic2l6ZSI6MjY3MDI0LCJrZXkiOiIiLCJhdXRob3IiOiJTZWVlZCBTdHVkaW8ifQ=="}}\n')

        # Call the model method
        model_info = self._device.model()

        # Assert that the query method was called with the correct command
        print(model_info)


if __name__ == '__main__':
    unittest.main()
