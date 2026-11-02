import logging
from functools import partial

from devtools.constants import CustomLogLevel

# named logger - its level and handler don't change the app's logging
logger = logging.getLogger("devtools")
# custom trace levels - logger.log skips the message when the level is off
logger.trace = partial(logger.log, CustomLogLevel.TRACE.value)
logger.base_trace = partial(logger.log, CustomLogLevel.BASE_TRACE.value)
logger.low_trace = partial(logger.log, CustomLogLevel.LOW_TRACE.value)

class LoggingUtils:
    # define the new levels
    logging.addLevelName(CustomLogLevel.TRACE.value, "trace")
    logging.addLevelName(CustomLogLevel.BASE_TRACE.value, "base_trace")
    logging.addLevelName(CustomLogLevel.LOW_TRACE.value, "low_trace")

    @staticmethod
    def set_logging_level(log_level=logging.INFO):
        logger.setLevel(log_level)
        # no propagate - else the app's handlers print devtools lines too
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
            logger.addHandler(handler)
        logger.propagate = False
