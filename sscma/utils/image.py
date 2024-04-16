import base64

import cv2
import numpy as np

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
