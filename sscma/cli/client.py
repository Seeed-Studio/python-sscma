import cv2
import click
import logging
import supervision as sv
import traceback

from sscma.micro.client import SerialClient, MQTTClient
from sscma.micro.device import Device
from sscma.micro.const import *
from sscma.utils.image import  image_from_base64

import time

logging.basicConfig(level=logging.CRITICAL)
valid_draw_options = ['boxes', 'color', 'label', 'circle', 'dot', 'triangle', 'ellipse',  'trace', 'heatmap']

@click.command()
@click.option('--broker', '-b', default=None, help='MQTT broker address')
@click.option('--username', '-u', default=None, help='MQTT username')
@click.option('--password', '-p', default=None, help='MQTT password')
@click.option('--device', '-d', default=None, help='Device ID')
@click.option('--port', '-p', default=None, help='Port to connect to')
@click.option('--baudrate',  '-b', default=921600, help='Baud rate for the serial connection')
@click.option('--headless', '-h', is_flag=True,  help='Show the image')
@click.option('--draw', '-d', multiple=True, type=click.Choice(valid_draw_options), default=['boxes'],  help='Draw options')
@click.option('--verbose', '-v', is_flag=True, help='Show the result')
def client(broker, username, password, device, port, baudrate, headless, draw, verbose):
    try:
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
        
        def on_monitor(device, msg):
            global key
            
            if "boxes" in msg:
            
                detections = sv.Detections.from_sscma_micro(msg)
                if verbose:
                    print(detections)
                    
                    
                if not headless:
                    frame = image_from_base64(msg["image"])
                    
                    annotated_frame = frame.copy()
                    
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
        
                    cv2.imshow("frame", annotated_frame)
                    if cv2.waitKey(1) & 0xFF == 27:
                       device.loop_stop()
            
        def on_connect(device):
            device.invoke(-1, False, True)
            click.echo("Device connected")
            click.echo("\nEnter'ESC' to exit\n")
            
        device.on_connect = on_connect
        device.on_monitor = on_monitor
        click.echo("Waiting for device to be ready")
        device.loop_start()
        while True:
            time.sleep(1)
            if not device.is_alive():
                break
            if device.status != DeviceStatus.READY:
                print(".", end="", flush=True)
                break
    except Exception as e:
        click.echo("Error: {}".format(e))
        traceback.print_exc()
        return