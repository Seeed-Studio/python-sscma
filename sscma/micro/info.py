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


from typing import Dict, Optional


class ModelInfo:
    """
    Represents information about a model.
    """

    def __init__(self, data):
        """
        Initializes a ModelInfo instance.

        Args:
            data (dict): The data containing model information.
        """

        if data is None:
            # create a dummy  unknown model
            data = {
                "uuid": 0x00000000,
                "name": "Unknown",
                "version": "0.0.0",
                "catagory": "Unknown",
                "model_type": "Unknown",
                "algoritm": "Unknown",
                "description": "Unknown",
                "image": "",
                "author": "Unknown",
                "token": "",
                "classes": "",
            }

        self.data = data

    def __repr__(self):
        """
        Returns a string representation of the ModelInfo instance.

        Returns:
            str: The string representation of the ModelInfo instance.
        """
        return "ModelInfo(name={}, version={})".format(
            self.name,
            self.version
        )

    @property
    def uuid(self) -> Optional[str]:
        """
        Returns the UUID of the model if available.

        Returns:
            str or None: The UUID of the model, or None if not available.
        """
        return self.data.get("uuid")

    @property
    def name(self) -> Optional[str]:
        """
        Returns the name of the model if available.

        Returns:
            str or None: The name of the model, or None if not available.
        """
        return self.data.get("name")

    @property
    def version(self) -> Optional[str]:
        """
        Returns the version of the model if available.

        Returns:
            str or None: The version of the model, or None if not available.
        """
        return self.data.get("version")

    @property
    def catagory(self) -> Optional[str]:
        """
        Returns the category of the model if available.

        Returns:
            str or None: The category of the model, or None if not available.
        """
        return self.data.get("catagory")

    @property
    def model_type(self) -> Optional[str]:
        """
        Returns the model type if available.

        Returns:
            str or None: The model type, or None if not available.
        """
        return self.data.get("model_type")

    @property
    def algoritm(self) -> Optional[str]:
        """
        Returns the algorithm of the model if available.

        Returns:
            str or None: The algorithm of the model, or None if not available.
        """
        return self.data.get("algoritm")

    @property
    def description(self) -> Optional[str]:
        """
        Returns the description of the model if available.

        Returns:
            str or None: The description of the model, or None if not available.
        """
        return self.data.get("description")

    @property
    def image(self) -> Optional[str]:
        """
        Returns the image of the model if available.

        Returns:
            str or None: The image of the model, or None if not available.
        """
        return self.data.get("image")

    @property
    def author(self) -> Optional[str]:
        """
        Returns the author of the model if available.

        Returns:
            str or None: The author of the model, or None if not available.
        """
        return self.data.get("author")

    @property
    def token(self) -> Optional[str]:
        """
        Returns the token of the model if available.

        Returns:
            str or None: The token of the model, or None if not available.
        """
        return self.data.get("token")

    @property
    def classes(self) -> Optional[str]:
        """
        Returns the classes of the model if available.

        Returns:
            str or None: The classes of the model, or None if not available.
        """
        return self.data.get("classes")

    @property
    def raw(self) -> Dict:
        """
        Returns the raw data of the model.

        Returns:
            dict: The raw data of the model.
        """
        return self.data

from typing import Dict, Optional

class MQTTInfo:
    """
    {
        "mqttserver": {
            "status": 0, 
            "config": {"client_id": "sscma_himax_we2_1", "address": "", "port": 0, "username": "", "password": "", "use_ssl": 0}
        },
        "mqttpubsub": {
            "config": {
                "pub_topic": "sscma/v0/himax_we2_1/tx", "pub_qos": 0, "sub_topic": "sscma/v0/himax_we2_1/rx", "sub_qos": 0}
            }
        }
    }
    """

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return "MQTTInfo(mqttserver={}, mqttpubsub={})".format(
            self.mqttserver,
            self.mqttpubsub
        )

    @staticmethod
    def construct(mqttserver, mqttpubsub):
        return {
            "mqttserver": mqttserver,
            "mqttpubsub": mqttpubsub,
        }

    @property
    def mqttserver(self) -> Optional[Dict]:
        """MQTT server information if available."""
        return self.data.get("mqttserver")

    @property
    def mqttpubsub(self) -> Optional[Dict]:
        """MQTT pubsub information if available."""
        return self.data.get("mqttpubsub")

    @property
    def server(self) -> Optional[Dict]:
        """MQTT server configuration if available."""
        return self.mqttserver.get("config")

    @property
    def pubsub(self) -> Optional[Dict]:
        """MQTT pubsub configuration if available."""
        return self.mqttpubsub.get("config")

    @property
    def address(self) -> Optional[str]:
        """MQTT server address if available."""
        return self.server.get("address")

    @property
    def port(self) -> Optional[int]:
        """MQTT server port if available."""
        return self.server.get("port")

    @property
    def username(self) -> Optional[str]:
        """MQTT server username if available."""
        return self.server.get("username")

    @property
    def password(self) -> Optional[str]:
        """MQTT server password if available."""
        return self.server.get("password")

    @property
    def use_ssl(self) -> Optional[int]:
        """MQTT server use_ssl if available."""
        return self.server.get("use_ssl")

    @property
    def pub_topic(self) -> Optional[str]:
        """MQTT pub_topic if available."""
        return self.pubsub.get("pub_topic")

    @property
    def pub_qos(self) -> Optional[int]:
        """MQTT pub_qos if available."""
        return self.pubsub.get("pub_qos")

    @property
    def sub_topic(self) -> Optional[str]:
        """MQTT sub_topic if available."""
        return self.pubsub.get("sub_topic")

    @property
    def sub_qos(self) -> Optional[int]:
        """MQTT sub_qos if available."""
        return self.pubsub.get("sub_qos")

    @property
    def raw(self):
        """Raw data as returned by the device."""
        return self.data

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