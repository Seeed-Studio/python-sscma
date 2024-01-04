from typing import List

import logging
from threading import Lock

import numpy as np
import cv2

from supervision import (
    ByteTrack,
    BoundingBoxAnnotator,
    LabelAnnotator,
    TraceAnnotator,
    PolygonZone,
    PolygonZoneAnnotator,
    HeatMapAnnotator,
    ColorPalette,
)

from sscma.utils.image import image_to_base64

from .utils import (
    SessionConfig,
    detection_to_tracked_bboxs,
    color_from_cmap,
)


class Pipeline:
    def __init__(self, config: SessionConfig):
        self.lock = Lock()

        tracker_config = config.tracker_config
        self.tracker = ByteTrack(
            track_thresh=tracker_config.track_thresh,
            track_buffer=tracker_config.track_buffer,
            match_thresh=tracker_config.match_thresh,
            frame_rate=tracker_config.frame_rate,
        )

        annotation_config = config.annotation_config
        self.canva_resolution = annotation_config.resolution[:2]
        self.canvas = {}
        self.canvas["background"] = np.zeros(
            (*self.canva_resolution, 4), dtype=np.uint8
        )
        polygon_canva = self.canvas["background"].copy()
        polygon_color_platte = ColorPalette.from_hex(color_from_cmap("Pastel2"))
        self.filter_regions = {}
        for i, (region_name, region_config) in enumerate(config.regions_config.items()):
            zone = PolygonZone(
                polygon=region_config.polygon,
                frame_resolution_wh=self.canva_resolution,
                triggering_position=region_config.triggering_position,
            )
            polygon_canva = PolygonZoneAnnotator(
                zone=zone,
                color=polygon_color_platte.by_idx(i),
                thickness=annotation_config.polygon.thickness,
                text_scale=annotation_config.polygon.text_scale,
                text_thickness=annotation_config.polygon.text_thickness,
                text_padding=annotation_config.polygon.text_padding,
            ).annotate(scene=polygon_canva, label=region_name)
            self.filter_regions[region_name] = zone
        self.canvas["polygon"] = polygon_canva

        color_platte = ColorPalette.from_hex(color_from_cmap("Accent"))
        self.box_annotator = BoundingBoxAnnotator(
            color=color_platte,
            thickness=annotation_config.bounding_box.thickness,
        )
        self.trace_annotator = TraceAnnotator(
            color=color_platte,
            position=annotation_config.tracing.position,
            trace_length=annotation_config.tracing.trace_length,
            thickness=annotation_config.tracing.trace_thickness,
        )
        self.label_annotator = LabelAnnotator(
            color=color_platte,
            text_scale=annotation_config.labeling.text_scale,
            text_thickness=annotation_config.labeling.text_thickness,
            text_padding=annotation_config.labeling.text_padding,
            text_position=annotation_config.labeling.text_position,
        )
        self.label_map = annotation_config.labeling.label_map
        self.heatmap_annontator = HeatMapAnnotator(
            position=annotation_config.heatmap.position,
            opacity=annotation_config.heatmap.opacity,
            radius=annotation_config.heatmap.radius,
            kernel_size=annotation_config.heatmap.kernel_size,
        )
        self.annotators = set(
            ["polygon", "bounding_box", "tracing", "labeling", "heatmap"]
        )

    def __annotate(self, detections: dict, annotator_name: str) -> np.ndarray:
        if annotator_name == "background":
            return self.canvas["background"]

        if annotator_name == "polygon":
            return self.canvas["polygon"]

        if annotator_name == "bounding_box":
            return self.box_annotator.annotate(
                scene=self.canvas["background"].copy(), detections=detections
            )

        if annotator_name == "tracing":
            return self.canvas["tracing"]

        if annotator_name == "labeling":
            return self.label_annotator.annotate(
                scene=self.canvas["background"].copy(),
                detections=detections,
                labels=[
                    f"#{tracker_id} {self.label_map[class_id] if class_id in self.label_map else class_id}"
                    for class_id, tracker_id in zip(
                        detections.class_id, detections.tracker_id
                    )
                ],
            )

        if annotator_name == "heatmap":
            return self.heatmap_annontator.annotate(
                scene=self.canvas["background"].copy()[:, :, :3], detections=detections
            )

        raise NotImplementedError(f"Annotator {annotator_name} is not implemented")

    def push(
        self,
        detections: dict,
        background: np.ndarray = None,
        annotations: List[List[str]] = None,
    ) -> dict:
        with self.lock:
            result = {"filtered_regions": {}, "annotations": [], "tracked_boxes": []}
            try:
                detections = self.tracker.update_with_detections(detections)

                result["filtered_regions"] = {
                    region_name: detections.tracker_id[
                        zone.trigger(detections)
                    ].tolist()
                    for region_name, zone in self.filter_regions.items()
                }
                result["annotations"] = []

                self.canvas["tracing"] = self.trace_annotator.annotate(
                    self.canvas["background"].copy(), detections=detections
                )

                if annotations is not None:
                    canvas = self.canvas.copy()
                    for annotation in annotations:
                        blending = (
                            background
                            if background is not None
                            else canvas["background"].copy()
                        )
                        w, h, c = blending.shape[:3]
                        for annotator in annotation:
                            if annotator not in self.annotators:
                                logging.warning(
                                    "Annotator %s is not implemented", annotator
                                )
                                continue
                            if annotator not in canvas:
                                canvas[annotator] = self.__annotate(
                                    detections, annotator
                                )
                            w, h, c = np.minimum(
                                canvas[annotator].shape[:3], blending.shape[:3]
                            )[:3]
                            blending = cv2.add(
                                blending[:w, :h, :c], canvas[annotator][:w, :h, :c]
                            )
                        if c == 4:
                            blending[
                                np.any(blending[:, :, :3] != 0, axis=-1), 3
                            ] = np.iinfo(blending.dtype).max
                        result["annotations"].append(image_to_base64(blending))

                result["tracked_boxes"] = detection_to_tracked_bboxs(detections)
            except Exception as exc:  # pylint: disable=broad-except
                logging.warning("Failed to track detections", exc_info=exc)
        return result
