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

```bash
sscma.cli --help
Usage: sscma.cli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  client
  flasher
  server
```

### Client

```bash
sscma.cli client --help
Usage: sscma.cli client [OPTIONS]

Options:
  -B, --broker TEXT       Specify the MQTT broker address
  -U, --username TEXT     Specify the MQTT username
  -P, --password TEXT     Specify the MQTT password
  -D, --device TEXT       Specify the Device ID
  -p, --port TEXT         Specify the Port to connect to
  -b, --baudrate INTEGER  Specify the Baudrate for the serial connection
  --sample                Enable the sample mode
  --invoke                Enable the invoke mode
  -s, --save              Enable the save mode
  -o, --save_dir TEXT     Specify the Directory for saveing images
  -h, --headless          Run the program without displaying the images
  -v, --verbose           Show detailed information during processin
  --help                  Show this message and exit.
```

#### Client with Serial

```bash
sscma.cli client ---port /dev/ttyUSB0 
```

#### Client with MQTT

```bash
sscma.cli client --broker mqtt.broker.com --username username --password password -device device_id 
```

#### Sample 

```bash
sscmai client --port /dev/ttyUSB0 --save 
```

### Flasher

```bash
sscma.cli flasher --help
Usage: sscma.cli flasher [OPTIONS]

Options:
  -p, --port TEXT         Port to connect to
  -f, --file TEXT         File to write to the device
  -b, --baudrate INTEGER  Baud rate for the serial connection
  -o, --offset TEXT       Offset to write the file to
  --help 
```

```bash
sscma.cli flasher -p /dev/ttyUSB0 -f firmware.bin 
```

## Contributing

If you have any idea or suggestion, please open an issue first.

If you want to contribute code, please fork this repository and submit a pull
request.

## License

MIT License
