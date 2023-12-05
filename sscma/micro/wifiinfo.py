from typing import Dict, Optional


class WiFiInfo:

    def __init__(self, data):
        """
        {
            "status": 0, 
            "in4_info": {"ip": "0.0.0.0", "netmask": "0.0.0.0", "gateway": "0.0.0.0"}, 
            "in6_info": {"ip": ":::::::", "prefix": ":::::::", "gateway": ":::::::"}, 
            "config": {"name_type": 0, "name": "xxxxxx", "security": 0, "password": "*******"}
        }
        """
        self.data = data

    def __repr__(self):
        return "WiFiInfo(status={}, IPv4={}, IPv6={}, config={})".format(
            self.status,
            self.IPv4,
            self.IPv6,
            self.config
        )

    @property
    def status(self) -> Optional[int]:
        """Status if available."""
        return self.data.get("status")

    @property
    def IPv4(self) -> Optional[Dict]:
        """IPv4 information if available."""
        return self.data.get("in4_info")

    @property
    def IPv6(self) -> Optional[Dict]:
        """IPv6 information if available."""
        return self.data.get("in6_info")

    @property
    def config(self) -> Optional[Dict]:
        """Configuration if available."""
        return self.data.get("config")

    @property
    def SSID(self) -> Optional[str]:
        """SSID if available."""
        return self.config.get("name")

    @property
    def password(self) -> Optional[str]:
        """Password if available."""
        return self.config.get("password")

    @property
    def encryption(self) -> Optional[int]:
        """Encryption if available."""
        return self.config.get("security")

    @property
    def raw(self):
        """Raw data as returned by the device."""
        return self.data
