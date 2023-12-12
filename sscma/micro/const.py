"""This module contains constants used in the SSCMA project.

Constants include response prefixes and suffixes, command types and names, error codes, MQTT parameters, and color constants.
"""

from enum import IntFlag
from typing import Final, Tuple

# all response begin with this prefix and end with this suffix
RESPONSE_PREFIX: Final[str] = b"\r{"
RESPONSE_SUFFIX: Final[str] = b"}\n"

# command types
CMD_PREFIX: Final[str] = "AT+"

CMD_TYPE_RESPONSE: Final[int] = 0
CMD_TYPE_EVENT: Final[int] = 1
CMD_TYPE_LOG: Final[int] = 2

# command names
CMD_AT_ID: Final[str] = "ID"
CMD_AT_NAME: Final[str] = "NAME"
CMD_AT_VERSION: Final[str] = "VER"
CMD_AT_STATS: Final[str] = "STAT"
CMD_AT_BREAK: Final[str] = "BREAK"
CMD_AT_RESET: Final[str] = "RST"
CMD_AT_WIFI: Final[str] = "WIFI"
CMD_AT_MQTTSERVER: Final[str] = "MQTTSERVER"
CMD_AT_MQTTPUBSUB: Final[str] = "MQTTPUBSUB"
CMD_AT_INVOKE: Final[str] = "INVOKE"
CMD_AT_SAMPLE: Final[str] = "SAMPLE"
CMD_AT_INFO: Final[str] = "INFO"
CMD_AT_TSCORE: Final[str] = "TSCORE"
CMD_AT_TIOU: Final[str] = "TIOU"
CMD_AT_ALGOS: Final[str] = "ALGOS"
CMD_AT_MODELS: Final[str] = "MODELS"
CMD_AT_MODEL: Final[str] = "MODEL"
CMD_AT_SENSORS: Final[str] = "SENSORS"
COMMADN_AT_ACTION: Final[str] = "ACTION"
CMD_AT_LED: Final[str] = "LED"

# command error codes
CMD_OK: Final[int] = 0
CMD_AGAIN: Final[int] = 1
CMD_ELOG: Final[int] = 2
CMD_ETIMEDOUT: Final[int] = 3
CMD_EIO: Final[int] = 4
CMD_EINVAL: Final[int] = 5
CMD_ENOMEM: Final[int] = 6
CMD_EBUSY: Final[int] = 7
CMD_ENOTSUP: Final[int] = 8
CMD_EPERM: Final[int] = 9
CMD_EUNKNOWN: Final[int] = 10


# command parameters
WIFI_ENC_AUTO: Final[int] = 0
WIFI_ENC_OPEN: Final[int] = 1
WIFI_ENC_WEP: Final[int] = 2
WIFI_ENC_WPA1_WPA2: Final[int] = 3
WIFI_ENC_WPA2_WPA3: Final[int] = 4
WIFI_ENC_WPA3: Final[int] = 5

# wifi status
WIFI_NO_JOINED: Final[int] = 0
WIFI_CONNECTING: Final[int] = 1
WIFI_JOINED: Final[int] = 2

# mqtt status
MQTT_NO_CONNECTED: Final[int] = 0
MQTT_CONNECTING: Final[int] = 1
MQTT_CONNECTED: Final[int] = 2

MQTT_QOS_0: Final[int] = 0
MQTT_QOS_1: Final[int] = 1
MQTT_QOS_2: Final[int] = 2

# event constants
EVENT_INVOKE: Final[str] = "INVOKE"
EVENT_SAMPLE: Final[str] = "SAMPLE"
EVENT_WIFI: Final[str] = "WIFI"
EVENT_MQTT: Final[str] = "MQTT"
EVENT_SUPERVISOR: Final[str] = "SUPERVISOR"

# log constants
LOG_AT: Final[str] = "AT"
LOG_LOG: Final[str] = "LOG"


class DeviceStatus(IntFlag):
    """Device status flags."""
    UNKNOWN = 0
    READY = 1
    SAMPLING = 2
    INVOKING = 4
    WIFI_CONNECTTING = 8
    WIFI_CONNECTED = 16
    MQTT_CONNECTTING = 32
    MQTT_CONNECTED = 64


# color constants
COLOR_RED: Final[Tuple[int, int, int]] = (255, 0, 0)
COLOR_GREEN: Final[Tuple[int, int, int]] = (0, 255, 0)
COLOR_BLUE: Final[Tuple[int, int, int]] = (0, 0, 255)
COLOR_YELLOW: Final[Tuple[int, int, int]] = (255, 255, 0)
COLOR_PURPLE: Final[Tuple[int, int, int]] = (255, 0, 255)
COLOR_CYAN: Final[Tuple[int, int, int]] = (0, 255, 255)
COLOR_WHITE: Final[Tuple[int, int, int]] = (255, 255, 255)
COLOR_BLACK: Final[Tuple[int, int, int]] = (0, 0, 0)
COLOR_ORANGE: Final[Tuple[int, int, int]] = (255, 165, 0)
COLOR_PINK: Final[Tuple[int, int, int]] = (255, 192, 203)
COLOR_GRAY: Final[Tuple[int, int, int]] = (128, 128, 128)
COLOR_BROWN: Final[Tuple[int, int, int]] = (165, 42, 42)
COLOR_GOLD: Final[Tuple[int, int, int]] = (255, 215, 0)
COLOR_SILVER: Final[Tuple[int, int, int]] = (192, 192, 192)
COLOR_MAROON: Final[Tuple[int, int, int]] = (128, 0, 0)
COLOR_OLIVE: Final[Tuple[int, int, int]] = (128, 128, 0)
COLOR_LIME: Final[Tuple[int, int, int]] = (0, 128, 0)
COLOR_TEAL: Final[Tuple[int, int, int]] = (0, 128, 128)
COLOR_NAVY: Final[Tuple[int, int, int]] = (0, 0, 128)
COLOR_AQUA: Final[Tuple[int, int, int]] = (0, 255, 255)
COLOR_INDIGO: Final[Tuple[int, int, int]] = (75, 0, 130)
COLOR_VIOLET: Final[Tuple[int, int, int]] = (238, 130, 238)

COLORS = [
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_YELLOW,
    COLOR_PURPLE,
    COLOR_CYAN,
    COLOR_WHITE,
    COLOR_BLACK,
    COLOR_ORANGE,
    COLOR_PINK,
    COLOR_GRAY,
    COLOR_BROWN,
    COLOR_GOLD,
    COLOR_SILVER,
    COLOR_MAROON,
    COLOR_OLIVE,
    COLOR_LIME,
    COLOR_TEAL,
    COLOR_NAVY,
    COLOR_AQUA,
    COLOR_INDIGO,
    COLOR_VIOLET
]
