from typing import Tuple, Union, Dict

import json
import base64

from dataclasses import dataclass
from functools import cache

import numpy as np
import cv2

from matplotlib import colormaps, colors
from supervision import Detections, Position

from sscma.hook.utils import xyxy_to_cxcywh


@cache
def color_from_cmap(cmap_name: str):
    cmap = colormaps[cmap_name]
    return [colors.rgb2hex(cmap(i)) for i in range(cmap.N)]


@dataclass
class TrackerConfig:
    track_thresh: float = 0.25
    track_buffer: int = 30
    match_thresh: float = 0.5
    frame_rate: int = 15

    def __post_init__(self):
        self.track_thresh = float(self.track_thresh)
        self.track_buffer = int(self.track_buffer)
        self.match_thresh = float(self.match_thresh)
        self.frame_rate = int(self.frame_rate)


@dataclass
class BoundingBoxConfig:
    thickness: int = 2

    def __post_init__(self):
        self.thickness = int(self.thickness)


@dataclass
class TracingConfig:
    position: Position = Position.CENTER
    trace_length: int = 30,
    trace_thickness: int = 2

    def __post_init__(self):
        self.position = Position(self.position)
        self.trace_length = int(self.trace_length)
        self.trace_thickness = int(self.trace_thickness)


@dataclass
class LabelingConfig:
    text_scale: float = 0.3
    text_thickness: int = 1
    text_padding: int = 3
    text_position: Position = Position.TOP_LEFT
    label_map: Union[Dict[int, str], Dict] = None

    def __post_init__(self):
        self.text_scale = float(self.text_scale)
        self.text_thickness = int(self.text_thickness)
        self.text_padding = int(self.text_padding)
        self.text_position = Position(self.text_position)
        if self.label_map is not None:
            self.label_map = {
                int(key): str(value) for key, value in self.label_map.items()
            }


@dataclass
class PolygonConfig:
    thickness: int = 1
    text_scale: float = 0.3
    text_thickness: int = 1
    text_padding: int = 3

    def __post_init__(self):
        self.thickness = int(self.thickness)
        self.text_scale = float(self.text_scale)
        self.text_thickness = int(self.text_thickness)
        self.text_padding = int(self.text_padding)


@dataclass
class HeatMapConfig:
    position: Position = Position.BOTTOM_CENTER
    opacity: float = 0.2
    radius: int = 10
    kernel_size: int = 5

    def __post_init__(self):
        self.position = Position(self.position)
        self.opacity = float(self.opacity)
        self.radius = int(self.radius)
        self.kernel_size = int(self.kernel_size)


@dataclass
class AnnotationConfig:
    resolution: Tuple[int, int]
    polygon: Union[PolygonConfig, Dict]
    bounding_box: Union[BoundingBoxConfig, Dict]
    tracing: Union[TracingConfig, Dict]
    labeling: Union[LabelingConfig, Dict]
    heatmap: Union[HeatMapConfig, Dict]

    def __post_init__(self):
        if len(self.resolution) != 2:
            raise ValueError("Resolution should have 2 elements")
        if self.resolution[0] < 64 or self.resolution[1] < 64:
            raise ValueError("Resolutions should be greater than 64")
        self.resolution = (int(self.resolution[0]), int(self.resolution[1]))
        self.polygon = PolygonConfig(**self.polygon)
        self.bounding_box = BoundingBoxConfig(**self.bounding_box)
        self.tracing = TracingConfig(**self.tracing)
        self.labeling = LabelingConfig(**self.labeling)
        self.heatmap = HeatMapConfig(**self.heatmap)


@dataclass
class Region:
    polygon: np.ndarray
    triggering_position: Position = Position.CENTER

    def __post_init__(self):
        self.polygon = np.asarray(self.polygon)
        self.triggering_position = Position(self.triggering_position)


@dataclass
class SessionConfig:
    tracker_config: Union[TrackerConfig, Dict]
    annotation_config: Union[AnnotationConfig, Dict]
    regions_config: Dict[str, Region]

    def __post_init__(self):
        self.tracker_config = TrackerConfig(**self.tracker_config)
        self.annotation_config = AnnotationConfig(**self.annotation_config)
        self.regions_config = {
            region_name: Region(**region_config)
            for region_name, region_config in self.regions_config.items()
        }


def parse_bytes_to_json(request: bytes) -> dict:
    try:
        request_json = json.loads(request)
        if not isinstance(request_json, dict):
            raise ValueError("Request should be a json dict")
        return request_json
    except Exception as exc:
        raise ValueError("Failed to parse bytes to json") from exc


def detection_to_tracked_bboxs(detection: Detections) -> list:
    cxcywhs = (
        np.round([xyxy_to_cxcywh(xyxy) for xyxy in detection.xyxy]).astype(int).tolist()
    )
    confidences = np.round(detection.confidence * 100.0).astype(int).tolist()
    class_ids = detection.class_id.astype(int).tolist()
    tracker_ids = detection.tracker_id.tolist()
    return [
        [*cxcywh, conf, class_id, tracker_id]
        for cxcywh, conf, class_id, tracker_id in zip(
            cxcywhs, confidences, class_ids, tracker_ids
        )
    ]


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
