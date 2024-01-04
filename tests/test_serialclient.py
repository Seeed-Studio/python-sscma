from sscma.micro.client import SerialClient
from sscma.micro.device import Device
from sscma.micro.const import *
import supervision as sv
import time
import logging
import signal
import numpy as np
import cv2
import base64

logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)

def image_from_base64(base64_image: str) -> np.ndarray:
    try:
        decoded = base64.b64decode(base64_image)
        image = np.frombuffer(decoded, dtype=np.uint8)
        if len(image) < 1:
            raise ValueError("Image is empty")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Failed to decode image")
    except Exception as exc:
        raise ValueError("Failed decode image from base64") from exc
    return image


def image_to_base64(image: np.ndarray, suffix: str = ".png") -> str:
    ret, img_bin = cv2.imencode(suffix, image)
    if not ret:
        raise ValueError("Failed to encode image to base64")
    base64_image = base64.b64encode(img_bin).decode("utf-8")
    return base64_image

client = SerialClient("COM46")
device = Device(client)
loop = True
tracker = sv.ByteTrack()
label_annotator = sv.LabelAnnotator(text_scale=0.3, text_padding=2)
box_annotator = sv.BoundingBoxAnnotator()
trace_annotator = sv.TraceAnnotator()

def monitor_handler(device, msg):
    frame = image_from_base64(msg["image"])
    detections = sv.Detections.from_sscma_micro(msg)
    detections = tracker.update_with_detections(detections)
    labels = [
    f"#{tracker_id} {device.model.classes[class_id]}"
        for class_id, tracker_id
        in zip(detections.class_id, detections.tracker_id)
    ]
    annotated_frame = box_annotator.annotate(
                scene=frame.copy(), detections=detections
            )
    annotated_frame = label_annotator.annotate(
        annotated_frame, detections=detections, labels=labels)
    annotated_frame = trace_annotator.annotate(
        annotated_frame, detections=detections)
    print(detections)
    cv2.imshow("frame", annotated_frame)
    cv2.waitKey(1)



def on_device_connect(device):
    print("device connected")
    device.Invoke(-1, False, True)
    device.tscore = 50
    device.tiou = 35


def signal_handler(signal, frame):
    print("Ctrl+C pressed!")
    device.loop_stop()
    exit(0)
   
def main():

    signal.signal(signal.SIGINT, signal_handler)


    device.on_monitor = monitor_handler
    device.on_connect = on_device_connect
     
    device.loop_start()

    print(device.info)

    i = 60

    while loop:
        # print(device.wifi)
        # print(device.mqtt)
        print(device.info)
        # print(device.model)


        time.sleep(2)


if __name__ == "__main__":
    main()
