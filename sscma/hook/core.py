import numpy as np
from supervision import Detections
from sscma.hook.utils import cxcywh_to_xyxy

@classmethod
def from_sscma_micro(cls: Detections, detection: dict) -> Detections:
    if "boxes" not in detection:
        raise ValueError("No boxes in detection")
    boxes = detection["boxes"]  # [x,y,w,h,conf,class_id]
    boxes = np.asarray(boxes)
    if len(boxes.shape) > 2:
        raise ValueError("Dimension of boxes should not be greater than 2")
    if len(boxes.shape) == 2 and boxes.shape[1] != 6:
        raise ValueError("Shape of boxes should be (N, 6) or empty")
    CONFIDENCE = 4
    CLASS_ID = 5
    LEN = len(boxes)
    xyxys = np.empty((LEN, 4))
    confidences = np.empty((LEN))
    class_ids = np.empty((LEN), dtype=int)
    for i, box in enumerate(boxes):
        xyxys[i] = cxcywh_to_xyxy(box)
        confidences[i] = box[CONFIDENCE] / 100.0
        class_ids[i] = box[CLASS_ID]
    return cls(xyxy=xyxys, confidence=confidences, class_id=class_ids)
