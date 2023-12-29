import numpy as np

def xywh_to_xyxy(xywh: np.ndarray) -> np.ndarray:
    xyxy = np.asarray(xywh[:4])
    xyxy[2:4] = xyxy[2:4] + xyxy[0:2]
    return xyxy


def xyxy_to_xywh(xyxy: np.ndarray) -> np.ndarray:
    xywh = np.asarray(xyxy[:4])
    xywh[2:4] = xywh[2:4] - xywh[0:2]
    return xywh


def cxcywh_to_xyxy(cxcywh: np.ndarray) -> np.ndarray:
    xyxy = np.asarray(cxcywh[:4])
    xyxy[0:2] = xyxy[0:2] - (xyxy[2:4] / 2.0)
    xyxy[2:4] = xyxy[0:2] + xyxy[2:4]
    return xyxy


def xyxy_to_cxcywh(xyxy: np.ndarray) -> np.ndarray:
    cxcywh = np.asarray(xyxy[:4])
    cxcywh[2:4] = cxcywh[2:4] - cxcywh[0:2]
    cxcywh[0:2] = cxcywh[0:2] + (cxcywh[2:4] / 2.0)
    return cxcywh
