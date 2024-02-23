from typing import List

from threading import Lock
from concurrent.futures import ThreadPoolExecutor, wait

from os import sched_getaffinity
import numpy as np

from supervision import (
    Detections,
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
        self.tracker_lock = Lock()
        self.tracing_lock = Lock()

        cores = len(sched_getaffinity(0))
        self.pool = ThreadPoolExecutor(max_workers=cores)

        tracker_config = config.tracker_config
        self.tracker = ByteTrack(
            track_thresh=tracker_config.track_thresh,
            track_buffer=tracker_config.track_buffer,
            match_thresh=tracker_config.match_thresh,
            frame_rate=tracker_config.frame_rate,
        )

        annotation_config = config.annotation_config
        self.canva_resolution = annotation_config.resolution[:2]
        self.canva_background = np.zeros((*self.canva_resolution, 3), dtype=np.uint8)
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
        self.canva_polygon = [polygon_canva, self.__mask_from_annotation(polygon_canva)]

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
            opacity=1.0,
            radius=annotation_config.heatmap.radius,
            kernel_size=annotation_config.heatmap.kernel_size,
        )
        self.canva_heatmap_weight = annotation_config.heatmap.opacity

    @staticmethod
    def __mask_from_annotation(annotation: np.ndarray) -> np.ndarray:
        mask = annotation > 0
        mask = np.any(mask, axis=-1)
        return mask

    @staticmethod
    def __overlay(
        background: np.ndarray, foreground: np.ndarray, mask: np.ndarray
    ) -> np.ndarray:
        background[mask] = foreground[mask]
        return background

    @staticmethod
    def __weighted_overlay(
        background: np.ndarray, foreground: np.ndarray, mask: np.ndarray, weight: float
    ) -> np.ndarray:
        background[mask] = background[mask] * (1.0 - weight) + foreground[mask] * weight
        return background

    def __annotate(self, name: str, detections: Detections):
        if name == "polygon":
            return self.canva_polygon.copy()

        if name == "bounding_box":
            annotated = self.box_annotator.annotate(
                scene=self.canva_background.copy(), detections=detections
            )
            mask = self.__mask_from_annotation(annotated)
            return [annotated, mask]

        if name == "tracing":
            with self.tracing_lock:
                annotated = self.trace_annotator.annotate(
                    scene=self.canva_background.copy(), detections=detections
                )
            mask = self.__mask_from_annotation(annotated)
            return [annotated, mask]

        if name == "labeling":
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
            mask = self.__mask_from_annotation(annotated)
            return [annotated, mask]

        if name == "heatmap":
            annotated = self.heatmap_annontator.annotate(
                scene=self.canva_background.copy(), detections=detections
            )
            mask = self.__mask_from_annotation(annotated)
            return [annotated, mask]

        raise NotImplementedError(f"Annotator {name} is not implemented")

    def __annotate_and_assign(self, name: str, detections: Detections, canvas: dict):
        canvas[name] = self.__annotate(name, detections)

    def push(
        self,
        detections: Detections,
        background: np.ndarray = None,
        annotations: List[List[str]] = None,
    ) -> dict:

        with self.tracker_lock:
            detections = self.tracker.update_with_detections(detections)

        filtered_regions = {
            region_name: detections.tracker_id[zone.trigger(detections)].tolist()
            for region_name, zone in self.filter_regions.items()
        }
        annotated_images = []
        result = {
            "filtered_regions": filtered_regions,
            "tracked_boxes": detection_to_tracked_bboxs(detections),
            "annotations": annotated_images,
        }

        if annotations is not None:
            has_background = background is not None
            canvas = {}
            for annotation in annotations:
                required = set(annotation) - set(canvas.keys())
                if len(required) > 0:
                    futures = [
                        self.pool.submit(self.__annotate_and_assign, name, detections, canvas)
                        for name in required
                    ]
                    wait(futures, return_when="ALL_COMPLETED")

                blending = (
                    background.copy()
                    if has_background
                    else self.canva_background.copy()
                )

                for name in annotation:
                    annotated, mask = canvas[name]
                    if name == "heatmap":
                        blending = self.__weighted_overlay(
                            blending, annotated, mask, self.canva_heatmap_weight
                        )
                    else:
                        blending = self.__overlay(blending, annotated, mask)

                annotated_images.append(image_to_base64(blending))

        return result
