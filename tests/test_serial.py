from sscma.micro.client import Client
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

recieve_thread_running = True


def recieve_thread(serial_port, client):
    while recieve_thread_running:
        if serial_port.in_waiting:
            msg = serial_port.read(serial_port.in_waiting)
            if msg != b'':
                client.on_recieve(msg)


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
    device.invoke(-1, False, True)
    device.tscore = 70
    device.tiou = 70


def signal_handler(signal, frame):
    print("Ctrl+C pressed!")
    global recieve_thread_running
    recieve_thread_running = False
    exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    serial_port = serial.Serial("COM83", 921600, timeout=0.1)
    client = Client(lambda msg: serial_port.write(msg))
    threading.Thread(target=recieve_thread, args=(
        serial_port, client)).start()

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
        device.tscore = i
        device.tiou = i
        i = i + 1
        if i > 100:
            i = 30

        time.sleep(2)


if __name__ == "__main__":
    main()
