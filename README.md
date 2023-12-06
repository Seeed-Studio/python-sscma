# Python SSCMA-Micro

## Description

This is a client for the
[sscma_micro](https://github.com/Seeed-Studio/sscma_micro), which is a
microcontroller at server for the [SSCMA](https://github.com/Seeed-Studio/SSCMA)
models.

More information about the sscma_micro can be found at
[here](https://github.com/Seeed-Studio/sscma_micro/blob/dev/docs/protocol/at_protocol.md)

## Usage

### Install

```bash
pip install python-sscma
```

```python
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


    device.set_wifi("xxxxxxxx", "xxxxxxxx")

    device.set_mqtt_server("192.168.199.1", 1883, "sscma", "micro")


    device.invoke = -1
    i = 30

    print(device.info)
    print(device.model)
    print(device.wifi)
    print(device.mqtt)

    while True:
        device.tscore = i
        device.tiou = i
        i = i + 1
        if i > 100:
            i = 30
        time.sleep(2)


if __name__ == "__main__":
    main()
```

## Contributing

If you have any idea or suggestion, please open an issue first.

If you want to contribute code, please fork this repository and submit a pull
request.

## License

MIT License
