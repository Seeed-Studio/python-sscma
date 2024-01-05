from sscma.micro.client import Client, SerialClient
from sscma.micro.device import Device
from sscma.micro.const import *
import serial
import threading
import time
import logging
import signal
import cv2
import base64
import numpy as np

logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)


def monitor_handler(device, msg):
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
    device.Invoke(-1, False, True)
    device.tscore = 50
    device.tiou = 35


client = SerialClient("/dev/ttyACM0")

def signal_handler(signal, frame):
    print("Ctrl+C pressed!")
    client.loop_stop()
   
def main():

    signal.signal(signal.SIGINT, signal_handler)
 
    device = Device(client)

    device.on_monitor = monitor_handler
    device.on_connect = on_device_connect
     
    device.loop_start()

    print(device.info)

    i = 60

    while True:
        print(device.wifi)
        print(device.mqtt)
        print(device.info)
        print(device.model)


        time.sleep(2)


if __name__ == "__main__":
    main()
