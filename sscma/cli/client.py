
import os
import time
import logging
import cv2
import click

from sscma.micro.client import SerialClient, MQTTClient
from sscma.micro.device import Device
from sscma.micro.const import *
from sscma.utils.image import  image_from_base64

logging.basicConfig(level=logging.WARNING)

@click.command()
@click.option('--broker', '-B', default=None, help='Specify the MQTT broker address')
@click.option('--username', '-U', default=None, help='Specify the MQTT username')
@click.option('--password', '-P', default=None, help='Specify the MQTT password')
@click.option('--device', '-D', default=None, help='Specify the Device ID')
@click.option('--port', '-p', default=None, help='Specify the Port to connect to')
@click.option('--baudrate',  '-b', default=921600, help='Specify the Baudrate for the serial connection')
@click.option('--sample', is_flag=True,  default=False, help='Enable the Sample mode, default is Invoke mode')
@click.option('--save', '-s', is_flag=True, default=False, help='Enable the save mode')
@click.option('--save_dir', '-o', default="save", help="Specify the Directory for saveing images")
@click.option('--headless', '-h', is_flag=True,  help='Run the program without displaying the images')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information during processin')
def client(broker, username, password, device, port, baudrate, sample, save, save_dir, headless, verbose):
    try:
        
        try:
            if int(save) > 0:
                if not os.path.exists(os.path.join(save_dir)):
                    os.mkdir(os.path.join(save_dir))
                if not os.path.exists(os.path.join(save_dir, 'raw')):
                    os.mkdir(os.path.join(save_dir, 'raw'))
            if int(save) > 1:
                if not os.path.exists(os.path.join(save_dir, 'annotated')):
                    os.mkdir(os.path.join(save_dir, 'annotated'))
        except Exception as e:
            click.echo("Error: {}".format(e))
            return
            
        
        if broker is not None:
            tx_topic = "sscma/v0/{}/rx".format(device)
            rx_topic = "sscma/v0/{}/tx".format(device)
            if port is None:
                port = '1883'
            client = MQTTClient(host=broker, port=int(port), tx_topic=tx_topic,
                            rx_topic=rx_topic, username=username, password=password)
        else:
            client = SerialClient(port, baudrate)
            
        
        device = Device(client)
        
        def on_monitor(device, msg):
            
                 
            if verbose or headless:
                data = msg
                del data["image"]
                click.echo(data)
               
            if not headless or save:
                try:
                    if "image" in msg:
                        frame = image_from_base64(msg["image"])
                        if save:
                            timestamp = int(time.time() * 1000) 
                            file_name = f"{save_dir}/image_{timestamp}.jpg"
                            cv2.imwrite(file_name, frame)
                        if not headless:
                            cv2.imshow("image", frame)
                            if cv2.waitKey(1) & 0xFF == 27:
                                device.loop_stop()
                except Exception as e:
                    return
            
            
        def on_connect(device):
            click.echo("Device connected")
            if not headless:
                click.echo("\nEnter'ESC' to exit\n")
            if sample:
                device.Sample(-1)
            else:
                device.Invoke(-1)
            
        def on_disconnect(device):
            click.echo("Device disconnected")
            
        def on_log(device, log):
            click.echo(log)

            
        device.on_connect = on_connect
        device.on_disconnect = on_disconnect
        device.on_monitor = on_monitor
        device.on_log = on_log
        click.echo("Waiting for device to be ready")
        device.loop_start()
        
        try:
            while True:
                time.sleep(2)
                if not device.is_alive():
                    click.echo("Exited")
                    break
        except KeyboardInterrupt:
            device.loop_stop()
    except Exception as e:
        click.echo("Error: {}".format(e))
        return
