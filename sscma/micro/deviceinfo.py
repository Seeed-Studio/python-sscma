from typing import Optional


class DeviceInfo:
    """
    {
        "id": "1",
        "name": "xxxx",
        "token": "None",
        "version": {
            "at_api": "v0",
            "software": "v2023.12.05",
            "hardware": "1"
        }
    }
    """

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return "DeviceInfo(id={}, name={}, token={}, version={})".format(
            self.id,
            self.name,
            self.token,
            self.version
        )

    @staticmethod
    def construct(id, name, token, version):
        return {
            "id": id,
            "name": name,
            "token": token,
            "version": version,
        }

    @property
    def id(self) -> Optional[str]:
        """ID if available."""
        return self.data.get("id")

    @property
    def token(self) -> Optional[str]:
        """Token if available."""
        return self.data.get("token")

    @property
    def version(self) -> Optional[str]:
        """Version if available."""
        return self.data.get("version")

    @property
    def at_api(self) -> Optional[str]:
        """AT API version if available."""
        return self.version.get("at_api")

    @property
    def software(self) -> Optional[str]:
        """Software version if available."""
        return self.version.get("software")

    @property
    def hardware(self) -> Optional[str]:
        """Hardware version if available."""
        return self.version.get("hardware")

    @property
    def name(self) -> Optional[str]:
        """Name if available."""
        return self.data.get("name")
