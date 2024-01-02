import supervision

from .supervision import from_sscma_micro

supervision.Detections.from_sscma_micro = from_sscma_micro
