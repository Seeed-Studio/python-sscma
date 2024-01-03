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
    ColorPalette,
)

from .utils import (
    SessionConfig,
    detection_to_tracked_bboxs,
    image_to_base64,
    color_from_cmap,
)


class Pipeline:
    def __init__(self, config: SessionConfig):
        self.lock = Lock()
        self.canva_shape = config.resolution[:2]
        tracker_config = config.tracker_config
        self.tracker = ByteTrack(
            track_thresh=tracker_config.track_thresh,
            track_buffer=tracker_config.track_buffer,
            match_thresh=tracker_config.match_thresh,
            frame_rate=tracker_config.frame_rate,
        )
        annotation_config = config.annotation_config
        color_platte = ColorPalette.from_hex(color_from_cmap("Accent"))
        self.box_annotator = BoundingBoxAnnotator(
            color=color_platte,
            thickness=annotation_config.bbox_thickness,
        )
        self.label_annotator = LabelAnnotator(
            color=color_platte,
            text_scale=annotation_config.bbox_text_scale,
            text_padding=annotation_config.bbox_text_padding,
        )
        self.labels = config.annotation_config.labels
        self.trace_annotator = TraceAnnotator(
            color=color_platte,
            position=config.trace_config.trace_position,
            trace_length=config.trace_config.trace_length,
            thickness=annotation_config.trace_line_thickness,
        )
        zone_overlay = np.zeros((*self.canva_shape, 4), dtype=np.uint8)
        color_platte = ColorPalette.from_hex(color_from_cmap("Pastel2"))
        self.filter_regions = {}
        for i, (region_name, region_config) in enumerate(config.filter_regions.items()):
            zone = PolygonZone(
                polygon=region_config.polygon,
                frame_resolution_wh=self.canva_shape,
                triggering_position=region_config.triggering_position,
            )
            zone_overlay = PolygonZoneAnnotator(
                zone=zone,
                color=color_platte.by_idx(i),
                thickness=annotation_config.polygon_thickness,
                text_scale=annotation_config.polygon_text_scale,
                text_padding=annotation_config.polygon_text_padding,
            ).annotate(scene=zone_overlay, label=region_name)
            self.filter_regions[region_name] = zone
        self.backgorund = zone_overlay

    def push(
        self, detections: dict, background: np.ndarray = None
    ) -> dict:
        with self.lock:
            result = {}
            try:
                detections = self.tracker.update_with_detections(detections)
                result["filtered_regions"] = {
                    region_name: detections.tracker_id[
                        zone.trigger(detections)
                    ].tolist()
                    for region_name, zone in self.filter_regions.items()
                }

                image = self.backgorund.copy()
                annotated_image = self.box_annotator.annotate(
                    scene=image, detections=detections
                )
                annotated_labeled_image = self.label_annotator.annotate(
                    scene=annotated_image,
                    detections=detections,
                    labels=[
                        f"#{tracker_id} {self.labels[class_id] if class_id in self.labels else class_id}"
                        for class_id, tracker_id in zip(
                            detections.class_id, detections.tracker_id
                        )
                    ],
                )
                traced_annotated_labeled_image = self.trace_annotator.annotate(
                    annotated_labeled_image, detections=detections
                )
                if background is not None:
                    w, h, c = background.shape[:3]
                    if c == 1:
                        traced_annotated_labeled_image = cv2.cvtColor(
                            traced_annotated_labeled_image, cv2.COLOR_RGBA2GRAY
                        )
                    traced_annotated_labeled_image = cv2.add(
                        background, traced_annotated_labeled_image[:w, :h, :c]
                    )
                else:
                    traced_annotated_labeled_image[
                        np.any(traced_annotated_labeled_image[:, :, :3] != 0, axis=-1),
                        3,
                    ] = 255
                result["tracked_boxes"] = detection_to_tracked_bboxs(detections)
                result["annotated_image"] = image_to_base64(
                    traced_annotated_labeled_image
                )
            except Exception as exc:  # pylint: disable=broad-except
                logging.warning("Failed to track detections", exc_info=exc)
        return result
