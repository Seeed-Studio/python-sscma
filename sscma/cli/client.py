
import os
import time
import logging

import cv2
import click
import supervision as sv

from sscma.micro.client import SerialClient, MQTTClient
from sscma.micro.device import Device
from sscma.micro.const import *
from sscma.utils.image import  image_from_base64
from sscma.hook.supervision import ClassAnnotartor

logging.basicConfig(level=logging.INFO)

valid_draw_options = ['boxes', 'color', 'label', 'circle', 'dot', 'triangle', 'ellipse',  'trace', 'heatmap']

@click.command()
@click.option('--broker', '-b', default=None, help='Specify the MQTT broker address')
@click.option('--username', '-u', default=None, help='Specify the MQTT username')
@click.option('--password', '-p', default=None, help='Specify the MQTT password')
@click.option('--device', '-d', default=None, help='Specify the Device ID')
@click.option('--port', '-p', default=None, help='Specify the Port to connect to')
@click.option('--baudrate',  '-b', default=921600, help='Specify the Baudrate for the serial connection')
@click.option('--save', '-s', type=click.Choice(['0', '1', '2']), default='0', help='Choose whether to save images. 0: Do not save, 1: Save the original image, 2: Save the original and annotated images.')
@click.option('--save_dir', '-o', default="save", help="Specify the Directory for saveing images")
@click.option('--headless', '-h', is_flag=True,  help='Run the program without displaying the images')
@click.option('--draw', '-d', multiple=True, type=click.Choice(valid_draw_options), default=['boxes'],  help='pecify the types of elements to draw in the image')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information during processin')
def client(broker, username, password, device, port, baudrate, save, save_dir, headless, draw, verbose):
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
        
        tracker = sv.ByteTrack()
        label_annotator = sv.LabelAnnotator(text_scale=0.4, text_padding=2)
        box_annotator = sv.BoundingBoxAnnotator()
        trace_annotator = sv.TraceAnnotator()
        heat_map_annotator = sv.HeatMapAnnotator()
        color_annotator = sv.ColorAnnotator()
        circle_annotator = sv.CircleAnnotator()
        dot_annotator = sv.DotAnnotator()
        triangle_annotator = sv.TriangleAnnotator()
        ellipse_annotator = sv.EllipseAnnotator()
        class_annotator = ClassAnnotartor()
        
        def on_monitor(device, msg):
            
            if "image" not in msg:
                return
               
            if not headless or int(save) > 0:
                try:
                    frame = image_from_base64(msg["image"])
                    annotated_frame = frame.copy()
                    if int(save) > 0:
                        timestamp = int(time.time() * 1000) 
                        file_name = f"{save_dir}/raw/image_{timestamp}.jpg"
                        cv2.imwrite(file_name, frame)
                except Exception as e:
                    return

            if "boxes" in msg:
                detections = sv.Detections.from_sscma_micro(msg)
                
                if verbose or headless:
                    click.echo(detections)
                    
                if 'boxes' in draw:
                    annotated_frame = box_annotator.annotate(
                        annotated_frame, detections=detections
                    )
                    
                if 'trace' in draw:
                    detections = tracker.update_with_detections(detections)
                    labels = [
                    f"#{tracker_id} {device.model.classes[class_id]}:{confidence:.2f}"
                        for class_id, tracker_id, confidence 
                        in zip(detections.class_id, detections.tracker_id, detections.confidence)
                    ]
                    annotated_frame = trace_annotator.annotate(
                        annotated_frame, detections=detections)
                else:
                    labels = [
                    f"{device.model.classes[class_id]}:{confidence:.2f}"
                        for class_id, confidence
                        in zip(detections.class_id, detections.confidence)
                    ] 
                
                if 'label' in draw:
                    annotated_frame = label_annotator.annotate(
                        annotated_frame, detections=detections, labels=labels)
                
                if 'heatmap' in draw:
                    annotated_frame = heat_map_annotator.annotate(
                            annotated_frame, detections=detections)
                
                if 'color' in draw:
                    annotated_frame = color_annotator.annotate(
                        annotated_frame, detections=detections)
                
                if 'circle' in draw:
                    annotated_frame = circle_annotator.annotate(
                        annotated_frame, detections=detections)
                        
                if 'dot' in draw:
                    annotated_frame = dot_annotator.annotate(
                        annotated_frame, detections=detections)
                    
                if 'triangle' in draw:
                    annotated_frame = triangle_annotator.annotate(
                        annotated_frame, detections=detections)
                        
                if 'ellipse' in draw:
                    annotated_frame = ellipse_annotator.annotate(
                        annotated_frame, detections=detections)
                       
            if "classes" in msg:
                classifications  = sv.Classifications.from_sscma_micro_cls(msg)
                if verbose or headless:
                    click.echo(classifications)
                    
                if not headless:
                    annotated_frame = class_annotator.annotate(
                        scene=annotated_frame, classifications=classifications, labels=device.model.classes
                    )
                
            if not headless or int(save) > 1:
                cv2.imshow("frame", annotated_frame)
                if int(save) > 1:
                    timestamp = int(time.time() * 1000) 
                    file_name = f"{save_dir}/annotated/image_{timestamp}.jpg"
                    cv2.imwrite(file_name, annotated_frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    device.loop_stop()
            
        def on_connect(device):
            click.echo("Device connected")
            click.echo("\nEnter'ESC' to exit\n")
            device.Invoke(-1, False, True)
            
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
