from typing import Dict, Optional


class DeviceInfo:

    def __init__(self, data):
        """
        {
            "id": "string",
            "token": "string",
            "version": dict,
            "wifi": {
                "ssid": "string",
                "encryption": int,
            }
        }
        """

        self.data = data

    def __repr__(self):
        return "{} {} ({}) - token: {}".format(
            self.id,
            self.firmware_version,
            self.mac_address,
            self.token,
        )

    @staticmethod
    def construct(id, token, version, wifi):
        return {
            "id": id,
            "token": token,
            "version": version,
            "wifi": wifi,
        }

    @property
    def id(self) -> Optional[str]:
        """ID if available."""
        return self.data.get("id")

    @property
    def version(self) -> Optional[str]:
        """Version if available."""
        return self.data.get("version")

    @property
    def wifi(self):
        """Information about connected wlan accesspoint.

        If unavailable, returns an empty dictionary.
        """
        return self.data.get("wifi", {})

    @property
    def firmware_version(self) -> Optional[str]:
        """Firmware version if available."""
        return self.version.get("software")

    @property
    def hardware_version(self) -> Optional[str]:
        """Hardware version if available."""
        return self.version.get("hardware")

    @property
    def mac_address(self) -> Optional[str]:
        """MAC address, if available."""
        return self.data.get("mac")

    @property
    def token(self) -> Optional[str]:
        """Return the current device token."""
        return self.data.get("token")

    @property
    def raw(self):
        """Raw data as returned by the device."""
        return self.data
