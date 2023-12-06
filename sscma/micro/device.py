import os
import io
import json
import base64
import logging
from typing import Optional  # noqa: F401
from PIL import Image, ImageDraw, ImageFont, ImageFile

from .const import *
from .client import Client
from .modelinfo import ModelInfo
from .deviceinfo import DeviceInfo
from .wifiinfo import WiFiInfo
from .mqttinfo import MQTTInfo

_LOGGER = logging.getLogger(__name__)


class Device:
    """
    Represents a device that can communicate with the SSCMA system.
    """

    retry_count = 3
    timeout = 5

    def __init__(self,
                 client: Client = None,
                 debug: int = 0,
                 monitor_handler=None,
                 log_handler=None,
                 ) -> None:

        self._client = client

        self._info: Optional[DeviceInfo] = None
        self._model: Optional[ModelInfo] = None
        self._wifi: Optional[WiFiInfo] = None
        self._mqtt: Optional[MQTTInfo] = None

        self._debug = debug

        self._monitor_handler = monitor_handler
        self._log_handler = log_handler

        self._font_path = os.path.join(
            os.path.dirname(__file__), "../", "fonts", "Arial.ttf")

        self._status = DeviceStatus.UNKNOWN

        self._invoke = 0  # invoke times
        self._sample = 0  # sample times

        self.initialize()

    def check_status(status):
        """Decorator to check if the device is ready."""

        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if ((status & DeviceStatus.READY) == DeviceStatus.READY) and not (self._status & DeviceStatus.READY) == DeviceStatus.READY:
                    self.initialize()
                if not (self._status & status) == status:
                    _LOGGER.debug("Device status is not satisfied:{} & {}".format(
                        self._status, status))
                    return None  # Or raise an exception or handle as needed

                return func(self, *args, **kwargs)

            return wrapper

        return decorator

    def initialize(self):
        """Initialize the device."""
        if self._status & DeviceStatus.READY:
            return

        self.Break()

        self._info = self._fetch_info()
        if self._info is None:
            self._status = DeviceStatus.UNKNOWN
            return

        self._wifi_changed = False
        self._mqtt_changed = False

        self._wifi = self._fetch_wifi()
        self._mqtt = self._fetch_mqtt()
        self._model = self._fetch_model()

        self._client.set_event_handler(self._event_process)
        self._client.set_log_handler(self._log_process)

        self._status |= DeviceStatus.READY

        return self._status

    @property
    def status(self) -> int:
        """Return the status of the device."""
        return self._status

    @property
    def ready(self) -> bool:
        """Return True if the device is ready."""
        return self._status & DeviceStatus.READY

    @property
    def network_connected(self) -> bool:
        """Return True if the device is connected to the network."""
        return self._status & DeviceStatus.WIFI_CONNECTED

    @property
    def mqtt_connected(self) -> bool:
        """Return True if the device is connected to the MQTT broker."""
        return self._status & DeviceStatus.MQTT_CONNECTED

    @property
    @check_status(DeviceStatus.READY)
    def info(self, *, skip_cache=False) -> DeviceInfo:

        if self._info is not None and not skip_cache:
            return self._info

        self._info = self._fetch_info()
        return self._info

    @property
    @check_status(DeviceStatus.READY)
    def wifi(self, *, skip_cache=False) -> WiFiInfo:
        """
        Gets the wifi of the device.
        """

        if self._wifi is not None and not skip_cache and not self._wifi_changed:
            return self._wifi

        self._wifi = self._fetch_wifi()
        return self._wifi

    @property
    @check_status(DeviceStatus.READY)
    def mqtt(self, *, skip_cache=False) -> MQTTInfo:
        """
        Gets the mqtt of the device.
        """

        if self._mqtt is not None and not skip_cache and not self._mqtt_changed:
            return self._mqtt

        self._mqtt = self._fetch_mqtt()
        return self._mqtt

    @property
    @check_status(DeviceStatus.READY)
    def model(self, *, skip_cache=False) -> ModelInfo:

        if self._model is not None and not skip_cache:
            return self._model

        self._model = self._fetch_model()

        return self._model

    def Break(self) -> None:
        """Break the device."""
        self._client.execute(CMD_AT_BREAK)
        self._status &= ~DeviceStatus.SAMPLING
        self._status &= ~DeviceStatus.INVOKING

    def Reset(self) -> None:
        """Reset the device."""
        self._client.execute(CMD_AT_RESET)
        self._status &= ~DeviceStatus.SAMPLING
        self._status &= ~DeviceStatus.INVOKING

    @property
    @check_status(DeviceStatus.READY)
    def sample(self):
        """
        Gets the sample of the device.
        """
        response = self._client.get(CMD_AT_SAMPLE)
        if response is not None and response["code"] == CMD_OK:
            return response["data"]
        else:
            return None

    @sample.setter
    @check_status(DeviceStatus.READY)
    def sample(self, value):
        """
        Sets the sample of the device.
        """
        response = self._client.set(CMD_AT_SAMPLE, '{}'.format(value))
        if response is not None and response["code"] == CMD_OK:
            self._sample = value
            if value != 0:
                self._status |= DeviceStatus.SAMPLING
                self._status &= ~DeviceStatus.INVOKING
            return response["data"]
        else:
            return None

    @property
    @check_status(DeviceStatus.READY)
    def invoke(self):
        """
        Gets the invoke of the device.
        """
        response = self._client.get(CMD_AT_INVOKE)
        if response is not None and response["code"] == CMD_OK:
            return response["data"]
        else:
            return None

    @invoke.setter
    @check_status(DeviceStatus.READY)
    def invoke(self, value, filter=False, show=True):
        """
        Sets the invoke of the device.
        """
        response = self._client.set(CMD_AT_INVOKE, '{},{},{}'.format(
            value, 1 if filter else 0, 0 if show else 1))
        if response is not None and response["code"] == CMD_OK:
            self._invoke = value
            if value != 0:
                self._status |= DeviceStatus.INVOKING
                self._status &= ~DeviceStatus.SAMPLING
            return response["data"]
        else:
            return None

    @property
    @check_status(DeviceStatus.READY | DeviceStatus.INVOKING)
    def tscore(self):
        """
        Gets the tscore of the device.
        """
        response = self._client.get(CMD_AT_TSCORE)
        if response is not None and response["code"] == CMD_OK:
            return response["data"]
        else:
            return None

    @tscore.setter
    @check_status(DeviceStatus.READY | DeviceStatus.INVOKING)
    def tscore(self, value):
        """
        Sets the tscore of the device.
        """
        response = self._client.set(CMD_AT_TSCORE, '{}'.format(value))
        if response is not None and response["code"] == CMD_OK:
            return response["data"]
        else:
            return None

    @property
    @check_status(DeviceStatus.READY | DeviceStatus.INVOKING)
    def tiou(self):
        """
        Gets the tiou of the device.
        """
        response = self._client.get(CMD_AT_TIOU)
        if response is not None and response["code"] == CMD_OK:
            return response["data"]
        else:
            return None

    @tiou.setter
    @check_status(DeviceStatus.READY | DeviceStatus.INVOKING)
    def tiou(self, value):
        """
        Sets the tiou of the device.
        """
        response = self._client.set(CMD_AT_TIOU, '{}'.format(value))
        if response is not None and response["code"] == CMD_OK:
            return response["data"]
        else:
            return None

    @check_status(DeviceStatus.READY)
    def set_wifi(self, ssid, password, enc=WIFI_ENC_AUTO):
        """
        Sets the wifi of the device.
        """
        self._wifi_changed = True
        response = self._client.set(
            CMD_AT_WIFI, '"{}",{},"{}"'.format(ssid, enc, password))
        if response is not None and response["code"] == CMD_OK:
            self._status |= DeviceStatus.WIFI_CONNECTTING
            return response["data"]
        else:
            return None

    @check_status(DeviceStatus.READY)
    def set_mqtt_server(self, address, port=1883, user="", password="", client_id="", ssl=0):
        """
        Sets the mqtt of the device.

        Args:
        - address: mqtt broker address
        - user: mqtt broker user.
        - password: mqtt broker password.
        - ssl: whether to use ssl.
        """
        self._mqtt_changed = True
        
        response = self._client.set(
            CMD_AT_MQTTSERVER, '"{}","{}",{},"{}","{}",{}'.format(client_id, address, port, user, password, ssl))
        if response is not None and response["code"] == CMD_OK:
            self._status |= DeviceStatus.MQTT_CONNECTTING
            return response["data"]
        else:
            return None

    def _fetch_info(self) -> DeviceInfo:
        """Fetch device info from the device."""
        id = self._client.get(CMD_AT_ID, 2)
        if id is None or id["data"] == "":
            self._status = DeviceStatus.UNKNOWN
            return None
        name = self._client.get(CMD_AT_NAME, 2)
        if name is None or name["data"] == "":
            self._status = DeviceStatus.UNKNOWN
            return None

        version = self._client.get(CMD_AT_VERSION, 2)
        if version is None or version["data"] == "":
            self._status = DeviceStatus.UNKNOWN
            return None

        return DeviceInfo(DeviceInfo.construct(id["data"], name["data"], None, version["data"]))

    def _fetch_wifi(self) -> WiFiInfo:
        """Fetch wifi info from the device."""
        wifi = self._client.get(CMD_AT_WIFI)
        if wifi is not None and wifi["code"] == CMD_OK:
            if wifi["data"]["status"] != WIFI_NO_JOINED:
                self._status |= DeviceStatus.WIFI_CONNECTED
            else:
                self._status &= ~DeviceStatus.WIFI_CONNECTED
        self._wifi_changed = False
        return WiFiInfo(wifi["data"])

    def _fetch_mqtt(self) -> MQTTInfo:
        """Fetch mqtt info from the device."""
        server = self._client.get(CMD_AT_MQTTSERVER)
        if server is not None and server["code"] == CMD_OK:
            if server["data"]["status"] != MQTT_NO_CONNECTED:
                self._status |= DeviceStatus.MQTT_CONNECTED
            else:
                self._status &= ~DeviceStatus.MQTT_CONNECTED
        pubsub = self._client.get(CMD_AT_MQTTPUBSUB)
        self._mqtt_changed = False
        return MQTTInfo(MQTTInfo.construct(server["data"], pubsub["data"]))

    def _fetch_model(self) -> ModelInfo:
        """Fetch model info from the device."""
        response = self._client.get(CMD_AT_INFO, tag=False)

        if response is None or response["data"]["info"] == "":
            return ModelInfo(None)
        try:
            model = json.loads(base64.b64decode(response["data"]["info"]))
        except Exception as ex:
            self._status = DeviceStatus.UNKNOWN
            _LOGGER.error("fetch model exception:{}".format(ex))
            return None

        return ModelInfo(model)

    def _draw_classes(self, image, classes):
        """
        Draws classes on an image.

        Args:
        image: The image to draw the classes on.
        classes: The classes to draw.
        """

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        transp = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(transp, "RGBA")

        img_w, img_h = image.size

        num_classes = len(classes)
        rect_bottom = img_h / 10
        font_size = img_w / 16

        for i, (score, target) in enumerate(classes):

            target_str = self._model.classes[target] if target < len(
                self._model.classes) else str(target)
            alpha = 0.3
            fill_color = COLORS[target % len(COLORS)]
            rect_left = (img_w / num_classes) * i
            rect_right = (img_w / num_classes) * (i + 1)
            draw.rectangle([rect_left, 0, rect_right, rect_bottom],
                           fill=(*fill_color, int(255 * alpha)))
            font = ImageFont.truetype(self._font_path, size=font_size)
            text_left = (img_w / num_classes) * i
            text_top = rect_bottom - \
                font_size if rect_bottom >= font_size else rect_bottom + font_size
            draw.text((text_left, text_top),
                      f"{target_str}: {score}", fill="#ffffff", font=font)
            image.paste(Image.alpha_composite(image, transp))

        return image

    def _draw_boxes(self, image, boxes):
        """
        Draws boxes on an image.

        Args:
        image: The image to draw the boxes on.
        boxes: The boxes to draw.
        """

        img_w, img_h = image.size
        draw = ImageDraw.Draw(image)

        for box in boxes:
            x, y, w, h, score, target = box

            target_str = self._model.classes[target] if target < len(
                self._model.classes) else str(target)
            fill_color = COLORS[target % len(COLORS)]
            rect_left = x - w / 2
            rect_right = x + w / 2
            rect_top = y - h / 2
            rect_bottom = y + h / 2
            draw.rectangle([rect_left, rect_top, rect_right,
                           rect_bottom], outline=fill_color,  width=2)
            font_size = min(img_w, img_h) / 16
            font = ImageFont.truetype(self._font_path, int(font_size))
            text_color = "#ffffff"
            text_left = rect_left
            text_top = rect_top - font_size
            draw.rectangle([text_left, text_top, rect_right,
                           text_top + font_size], fill=fill_color)
            draw.text((text_left, text_top),
                      f"{target_str}: {score}", fill=text_color, font=font)

        return image

    def _draw_keypoints(self, image, keypoints):
        """
        Draws keypoints on an image.

        Args:
        image: The image to draw the keypoints on.
        keypoints: The keypoints to draw.
        """
        draw = ImageDraw.Draw(image)

        for point in keypoints:
            x, y, _, t = point
            # Use x value for color differentiation
            fill_color = COLORS[t % len(COLORS)]
            draw.point([x, y], fill=fill_color)

        return image

    def _event_process(self, event):
        """Process an event."""

        try:
            if EVENT_WIFI in event["name"]:
                if event["code"] == CMD_OK and event["data"]["status"] != WIFI_NO_JOINED:
                    self._status |= DeviceStatus.WIFI_CONNECTED
                else:
                    self._status &= ~DeviceStatus.WIFI_CONNECTED

                if EVENT_SUPERVISOR not in event["name"]:
                    self._status &= ~DeviceStatus.WIFI_CONNECTTING

            if EVENT_MQTT in event["name"]:

                if event["code"] == CMD_OK and event["data"]["status"] != MQTT_NO_CONNECTED:
                    self._status |= DeviceStatus.MQTT_CONNECTED
                else:
                    self._status &= ~DeviceStatus.MQTT_CONNECTED

                if EVENT_SUPERVISOR not in event["name"]:
                    self._status &= ~DeviceStatus.MQTT_CONNECTTING

            if EVENT_INVOKE in event["name"]:
                if self._invoke != -1:
                    self._invoke -= 1

                if self._invoke == 0:
                    self._status &= ~DeviceStatus.INVOKING

            if EVENT_SAMPLE in event["name"]:
                if self._sample != -1:
                    self._sample -= 1

                if self._sample == 0:
                    self._status &= ~DeviceStatus.SAMPLING

            if self._monitor_handler is not None and "image" in event["data"]:

                if event["data"]["image"] == "":
                    self._monitor_handler(None, reply)
                    return

                ImageFile.LOAD_TRUNCATED_IMAGES = True
                image = Image.open(io.BytesIO(
                    base64.b64decode(event["data"]["image"])))

                reply = event["data"]

                del reply["image"]

                if "classes" in event["data"]:
                    image = self._draw_classes(image, event["data"]["classes"])

                if "boxes" in event["data"]:
                    image = self._draw_boxes(image, event["data"]["boxes"])

                if "points" in event["data"]:
                    image = self._draw_keypoints(
                        image, event["data"]["keypoints"])

                self._monitor_handler(image, reply)

                return

        except Exception as ex:

            self._status = DeviceStatus.UNKNOWN
            _LOGGER.error("event process exception:{}".format(ex))

        return

    def _log_process(self, log):
        """Process a log."""
        if self._log_handler is not None:
            self._log_handler(log)