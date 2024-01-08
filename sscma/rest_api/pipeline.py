from typing import List, Dict

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
        self.canva_background = np.zeros((*self.canva_resolution, 4), dtype=np.uint8)
        self.canvas = {}
        polygon_canva = self.canva_background.copy()
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
        self.canvas["polygon"] = self.__masked_annotation(polygon_canva)

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

    def __masked_annotation(self, annotation: np.ndarray) -> np.ndarray:
        alpha = np.iinfo(annotation.dtype).max
        annotation[np.any(annotation[:, :, :3] != 0, axis=-1), 3] = alpha
        return annotation

    def __overlay(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        mask = foreground[:, :, 3] > 0
        background[mask] = foreground[mask]
        return background

    def __annotate(
        self,
        canvas: Dict[str, np.ndarray],
        name: str,
        detections: dict,
        blending: np.ndarray = None,
    ) -> np.ndarray:
        if name == "polygon":
            annotated = self.canvas["polygon"]
            if "polygon" not in canvas:
                canvas["polygon"] = annotated
            blending = self.__overlay(blending, annotated)
            return blending

        if name == "bounding_box":
            if "bounding_box" not in canvas:
                annotated = self.box_annotator.annotate(
                    scene=self.canva_background.copy(), detections=detections
                )
                annotated = self.__masked_annotation(annotated)
                canvas["bounding_box"] = annotated
            else:
                annotated = canvas["bounding_box"]
            blending = self.__overlay(blending, annotated)
            return blending

        if name == "tracing":
            if "tracing" not in canvas:
                annotated = self.trace_annotator.annotate(
                    scene=self.canva_background.copy(), detections=detections
                )
                annotated = self.__masked_annotation(annotated)
                canvas["tracing"] = annotated
            else:
                annotated = canvas["tracing"]
            blending = self.__overlay(blending, annotated)
            return blending

        if name == "labeling":
            if "labeling" not in canvas:
                annotated = self.label_annotator.annotate(
                    scene=self.canva_background.copy(),
                    detections=detections,
                    labels=[
                        f"#{tracker_id} {self.label_map[class_id] if class_id in self.label_map else class_id}"
                        for class_id, tracker_id in zip(
                            detections.class_id, detections.tracker_id
                        )
                    ],
                )
                annotated = self.__masked_annotation(annotated)
                canvas["labeling"] = annotated
            else:
                annotated = canvas["labeling"]
            blending = self.__overlay(blending, annotated)
            return blending

        if name == "heatmap":
            annotated = self.canva_background.copy()
            annotated[:, :, :3] = self.heatmap_annontator.annotate(
                scene=blending[:, :, :3], detections=detections
            )
            annotated = self.__masked_annotation(annotated)
            blending = annotated
            return blending

        raise NotImplementedError(f"Annotator {name} is not implemented")

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

                if annotations is not None:
                    background = (
                        cv2.cvtColor(background, cv2.COLOR_BGR2BGRA)
                        if background is not None
                        else self.canva_background
                    )
                    canvas_cache = {}
                    for annotation in annotations:
                        blending = background.copy()
                        for annotator in annotation:
                            blending = self.__annotate(
                                canvas=canvas_cache,
                                name=annotator,
                                detections=detections,
                                blending=blending,
                            )
                        result["annotations"].append(image_to_base64(blending))

                result["tracked_boxes"] = detection_to_tracked_bboxs(detections)
            except Exception as exc:  # pylint: disable=broad-except
                logging.warning("Failed to track detections", exc_info=exc)
        return result
