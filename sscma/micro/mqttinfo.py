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
