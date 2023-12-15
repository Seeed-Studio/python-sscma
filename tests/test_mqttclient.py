import paho.mqtt.client as mqtt
import time

from sscma.micro.client import MQTTClient
from sscma.micro.device import Device
from sscma.micro.const import *
import serial
import threading
import time
import logging
import cv2
import base64
import numpy as np


logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)


# 定义代理服务器和主题
broker_address = "192.168.199.230"
rx_topic = "sscma/v0/grove_vision_ai_we2_360779f5/tx"
tx_topic = "sscma/v0/grove_vision_ai_we2_360779f5/rx"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(rx_topic)


def on_message(client, tclient, msg):
    tclient.on_recieve(msg.payload)


def monitor_handler(msg):

    if "image" in msg:
        jpeg_bytes = base64.b64decode(msg["image"])

        # Convert the bytes into a numpy array
        nparr = np.frombuffer(jpeg_bytes, np.uint8)

        # Decode the image array using OpenCV
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Display the image
        cv2.imshow('Base64 Image', img)
        cv2.waitKey(1)
        msg.pop("image")

    print(msg)


def on_device_connect(device):
    print("device connected")
    device.invoke(-1, False, True)
    device.tscore = 70
    device.tiou = 70


def main():

    client = MQTTClient(host=broker_address, port=1883, tx_topic=tx_topic,
                        rx_topic=rx_topic, username="user", password="user")
    device = Device(client)
    device.on_monitor = monitor_handler
    device.on_connect = on_device_connect
    device.loop_start()

    i = 60
    while True:
        print("model:{}".format(device.model))
        # device.tscore = i
        # device.tiou = i
        # i = i + 1
        # if i > 100:
        #     i = 30

        time.sleep(2)


if __name__ == "__main__":
    main()
