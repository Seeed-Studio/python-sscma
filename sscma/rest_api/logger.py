import logging
import traceback


class Formatter(logging.Formatter):
    def formatException(self, ei):
        type_, value_, traceback_ = ei
        if logger.getEffectiveLevel() == logging.DEBUG:
            return "".join(traceback.format_exception(type_, value_, traceback_))
        return f"{type_.__name__}: {value_}"


logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = Formatter("%(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
