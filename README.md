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
  -b, --broker TEXT               Specify the MQTT broker address
  -u, --username TEXT             Specify the MQTT username
  -p, --password TEXT             Specify the MQTT password
  -d, --device TEXT               Specify the Device ID
  -p, --port TEXT                 Specify the Port to connect to
  -b, --baudrate INTEGER          Specify the Baudrate for the serial
                                  connection
  -s, --save [0|1|2]              Choose whether to save images. 0: Do not
                                  save, 1: Save the original image, 2: Save
                                  the original and annotated images.
  -o, --save_dir TEXT             Specify the Drectory for saveing images
  -h, --headless                  Run the program without displaying the
                                  images
  -d, --draw [boxes|color|label|circle|dot|triangle|ellipse|trace|heatmap]
                                  pecify the types of elements to draw in the
                                  image
  -v, --verbose                   Show detailed information during processin
  --help 
```

#### Client with Serial

```bash
sscma.cli client -d /dev/ttyUSB0  -d boxes
```

#### Client with MQTT

```bash
sscma.cli client -b mqtt.broker.com -u username -p password -d device_id -d boxes
```

#### Sample 

```bash
sscmai client -d /dev/ttyUSB0  -d boxes --save 1
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

```
sscma.cli flasher -p /dev/ttyUSB0 -f firmware.bin 
```

### Server

```bash
sscma.cli server --help
Usage: sscma.cli server [OPTIONS]

Options:
  --host TEXT            Host to run the server on
  --port INTEGER         Port to run the server on
  --ssl                  Use SSL for the server
  --ssl-certfile TEXT    SSL certificate file
  --ssl-keyfile TEXT     SSL key file
  --max-workers INTEGER  Maximum number of worker threads
  --help                 Show this message and exit.
```
More information about the server can be found at [here](./docs/server.md)


## Contributing

If you have any idea or suggestion, please open an issue first.

If you want to contribute code, please fork this repository and submit a pull
request.

## License

MIT License
