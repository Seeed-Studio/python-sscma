from sscma.micro.client import Client
from sscma.micro.device import Device
from sscma.micro.const import *
import serial
import threading
import time
import logging
import signal

logging.basicConfig(level=logging.ERROR)

_LOGGER = logging.getLogger(__name__)

recieve_thread_running = True


def recieve_thread(serial_port, client):
    while recieve_thread_running:
        if serial_port.in_waiting:
            msg = serial_port.read(serial_port.in_waiting)
            if msg != b'':
                client.recieve_handler(msg)


def monitor_handler(image, msg):
    if image != None:
        image.show()
    print(msg)


def signal_handler(signal, frame):
    print("Ctrl+C pressed!")
    global recieve_thread_running
    recieve_thread_running = False
    exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    serial_port = serial.Serial("COM77", 921600, timeout=0.1)
    client = Client(lambda msg: serial_port.write(msg), debug=1)
    threading.Thread(target=recieve_thread, args=(
        serial_port, client)).start()

    time.sleep(0.2)

    device = Device(client, monitor_handler=monitor_handler, debug=1)

    print(device.info)

    device.set_wifi("airController", "xxxxxxxx")

    # while (device.status & DeviceStatus.WIFI_CONNECTTING != DeviceStatus.WIFI_CONNECTTING):
    #     print("Waiting for network connection...")
    #     time.sleep(1)

    # if (device.status & DeviceStatus.WIFI_CONNECTED == DeviceStatus.WIFI_CONNECTED):
    #     print("Network connection successful!")

    device.set_mqtt_server("192.168.6.162", 1883, "seeed", "xiao")

    #     while (device.status & DeviceStatus.MQTT_CONNECTTING == DeviceStatus.MQTT_CONNECTTING):
    #         print("Waiting for MQTT connection...")
    #         time.sleep(1)

    # if (device.status & DeviceStatus.MQTT_CONNECTED == DeviceStatus.MQTT_CONNECTED):
    #     print("MQTT connection successful!")

    # device.invoke = -1
    i = 30

    while True:
        print(device.wifi)
        print(device.mqtt)
        print(device.info)
        print(device.model)
        # device.tscore = i
        # device.tiou = i
        # i = i + 1
        # if i > 100:
        #     i = 30

        time.sleep(2)


if __name__ == "__main__":
    main()
