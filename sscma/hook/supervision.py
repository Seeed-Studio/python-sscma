
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np

from supervision import Detections, Classifications
from supervision.annotators.utils import ColorLookup, Position, get_color_by_index
from supervision.draw.color import Color, ColorPalette


from sscma.hook.utils import cxcywh_to_xyxy

@classmethod
def from_sscma_micro(cls: Detections, results: dict) -> Detections:
    if "boxes" not in results:
        raise ValueError("No boxes in detection")
    boxes = results["boxes"]  # [x,y,w,h,conf,class_id]
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

@classmethod
def from_sscma_micro_cls(cls: Classifications, results: dict) -> Classifications:
    if "classes" not in results:
        raise ValueError("No classes in detection")
    classes = results["classes"]  # [class_id, confidence]

    CONFIDENCE = 0
    CLASS_ID = 1
    LEN = len(classes)

    if LEN == 0:
        return cls(class_id=np.array([]), confidence=np.array([]))

    class_ids = np.empty((LEN), dtype=int)
    confidences = np.empty((LEN))

    for i, class_ in enumerate(classes):
        confidences[i] = class_[CONFIDENCE] / 100.0
        class_ids[i] = class_[CLASS_ID]


    return cls(class_id=class_ids, confidence=confidences)


class ClassAnnotartor():
    """
    A class for drawing class name and confidence on the image
    """

    def __init__(
        self,
        color: Union[Color, ColorPalette] = ColorPalette.DEFAULT,
        opacity: float = 0.5,
        text_color: Color = Color.WHITE,
        text_scale: float = 0.5,
        text_thickness: int = 1,
        text_padding: int = 5,
        color_lookup: ColorLookup = ColorLookup.CLASS,
    ):
        """
        Args:
            color (Union[Color, ColorPalette]): The color or color palette to use for
                annotating the text background.
            text_color (Color): The color to use for the text.
            text_scale (float): Font scale for the text.
            text_thickness (int): Thickness of the text characters.
            text_padding (int): Padding around the text within its background box.
            text_position (Position): Position of the text relative to the detection.
                Possible values are defined in the `Position` enum.
            color_lookup (str): Strategy for mapping colors to annotations.
                Options are `INDEX`, `CLASS`, `TRACK`.
        """
        self.color: Union[Color, ColorPalette] = color
        self.opacity: float = opacity
        self.text_color: Color = text_color
        self.text_scale: float = text_scale
        self.text_thickness: int = text_thickness
        self.text_padding: int = text_padding
        self.color_lookup: ColorLookup = color_lookup


    def annotate(
        self,
        scene: np.ndarray,
        classifications: Classifications,
        labels: List[str] = None,
    ) -> np.ndarray:

        """
        Annotates the given scene with labels based on the provided classifications.

        Args:
            scene (np.ndarray): The image where labels will be drawn.
            classifications (Classifications): classification to annotate.
            labels (List[str]): Optional. Custom labels for each detection.

        Returns:
            The annotated image.

        Example:
            ```python
            >>> import supervision as sv

            >>> image = ...
            >>> classifications = sv.Classifications(...)

            >>> class_annotator = sv.ClassAnnotartor()
            >>> annotated_frame = class_annotator.annotate(
            ...     scene=image.copy(),
            ...     classification=classifications
            ... )
            ```
        ![label-annotator-example](https://media.roboflow.com/
        supervision-annotator-examples/label-annotator-example-purple.png)
        """

        font = cv2.FONT_HERSHEY_SIMPLEX
        mask_image = scene.copy()
        for i, (class_id, confidnes) in enumerate(zip(classifications.class_id, classifications.confidence)):
            label = labels[class_id]
            color = get_color_by_index(color=self.color, idx=class_id)
            text = f"{label}: {confidnes:.2f}"
            text_size, _ = cv2.getTextSize(
                text, font, self.text_scale, self.text_thickness
            )
            text_width, text_height = text_size
            text_width += self.text_padding * 2
            text_height += self.text_padding * 2
            text_x, text_y = 0, text_height * (i+1)
            text_box_origin = (text_x, text_y - text_height)
            text_box_end = (text_x + text_width, text_y)
            cv2.rectangle(
                img=scene,
                pt1=text_box_origin,
                pt2=text_box_end,
                color=color.as_rgb(),
                thickness=-1
            )
            scene = cv2.addWeighted(
                scene, self.opacity, mask_image, 1 - self.opacity, gamma=0
            )
            cv2.putText(
                img=scene,
                text=text,
                org=(text_x + self.text_padding, text_y - self.text_padding),
                fontFace=font,
                fontScale=self.text_scale,
                color=self.text_color.as_rgb(),
                thickness=self.text_thickness,
                lineType=cv2.LINE_AA,
            )

        return scene
