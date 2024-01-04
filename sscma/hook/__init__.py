import supervision

from .supervision import from_sscma_micro, from_sscma_micro_cls

supervision.Detections.from_sscma_micro = from_sscma_micro
supervision.Classifications.from_sscma_micro_cls = from_sscma_micro_cls
