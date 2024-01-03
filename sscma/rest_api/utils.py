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


@dataclass
class TraceConfig:
    trace_position: Position = Position.CENTER
    trace_length: int = 30

    def __post_init__(self):
        self.trace_position = Position(self.trace_position)


@dataclass
class AnnotationConfig:
    labels: Union[Dict[int, str], Dict]
    bbox_thickness: int = 2
    bbox_text_scale: float = 0.3
    bbox_text_padding: int = 5
    polygon_thickness: int = 1
    polygon_text_scale: float = 0.3
    polygon_text_padding: int = 5
    trace_line_thickness: int = 2

    def __post_init__(self):
        labels = {}
        for key, value in self.labels.items():
            labels[int(key)] = str(value)
        self.labels = labels


@dataclass
class FilterRegion:
    polygon: np.ndarray
    triggering_position: Position = Position.CENTER

    def __post_init__(self):
        self.polygon = np.asarray(self.polygon)
        self.triggering_position = Position(self.triggering_position)


@dataclass
class SessionConfig:
    resolution: Tuple[int, int]
    tracker_config: Union[TrackerConfig, Dict]
    trace_config: Union[TraceConfig, Dict]
    annotation_config: Union[AnnotationConfig, Dict]
    filter_regions: Dict[str, FilterRegion]

    def __post_init__(self):
        if len(self.resolution) != 2:
            raise ValueError("Resolution should have 2 elements")
        if self.resolution[0] < 64 or self.resolution[1] < 64:
            raise ValueError("Resolutions should be greater than 64")
        self.tracker_config = TrackerConfig(**self.tracker_config)
        self.trace_config = TraceConfig(**self.trace_config)
        self.annotation_config = AnnotationConfig(**self.annotation_config)
        self.filter_regions = {
            region_name: FilterRegion(**region_config)
            for region_name, region_config in self.filter_regions.items()
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
