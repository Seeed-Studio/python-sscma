from sscma_micro.client import Client
from sscma_micro.device import Device
from sscma_micro.const import *
import serial
import threading
import time
import logging

logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)


def recieve_thread(serial_port, client):
    while True:
        if serial_port.in_waiting:
            msg = serial_port.read(serial_port.in_waiting)
            if msg != b'':
                client.recieve_handler(msg)


def monitor_handler(image, msg):
    # if image != None:
    #     image.show()
    print(msg)


def main():
    serial_port = serial.Serial("/dev/ttyACM0", 115200, timeout=0.1)
    client = Client(lambda msg: serial_port.write(msg), debug=1)
    threading.Thread(target=recieve_thread, args=(
        serial_port, client)).start()


    device = Device(client, monitor_handler=monitor_handler, debug=1)

    #device.set_wifi("Eureka", "31415926")
    

    # while (device.status & DeviceStatus.WIFI_CONNECTTING != DeviceStatus.WIFI_CONNECTTING):
    #     print("Waiting for network connection...")
    #     time.sleep(1)

    # if (device.status & DeviceStatus.WIFI_CONNECTED == DeviceStatus.WIFI_CONNECTED):
    #     print("Network connection successful!")

    #     device.set_mqtt_server("192.168.6.162", "seeed", "xiao")

    #     while (device.status & DeviceStatus.MQTT_CONNECTTING == DeviceStatus.MQTT_CONNECTTING):
    #         print("Waiting for MQTT connection...")
    #         time.sleep(1)
            
    # if (device.status & DeviceStatus.MQTT_CONNECTED == DeviceStatus.MQTT_CONNECTED):
    #     print("MQTT connection successful!")
            
    #     if device.set_mqtt_pubsub("test_tx", "test_rx") == None:
    #         print("MQTT pubsub failed!")
        

    device.invoke = -1
    i = 30

    while True:
        print(device.mqtt_pubsub)
        device.tscore = i
        device.tiou = i
        i = i + 1
        if i > 100:
            i = 30

        time.sleep(2)


if __name__ == "__main__":
    main()
