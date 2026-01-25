import logging

from devtools.constants import CustomLogLevel

class LoggingUtils:
    # define the new levels
    logging.addLevelName(CustomLogLevel.TRACE.value, "trace")
    logging.addLevelName(CustomLogLevel.BASE_TRACE.value, "base_trace")
    logging.addLevelName(CustomLogLevel.LOW_TRACE.value, "low_trace")

    @staticmethod
    def _low_trace(message, *args, **kwargs):
        if logging.getLogger().isEnabledFor(CustomLogLevel.LOW_TRACE.value):
            logging.log(CustomLogLevel.LOW_TRACE.value, message, *args, **kwargs)
    @staticmethod
    def _base_trace(message, *args, **kwargs):
        if logging.getLogger().isEnabledFor(CustomLogLevel.BASE_TRACE.value):
            logging.log(CustomLogLevel.BASE_TRACE.value, message, *args, **kwargs)
    @staticmethod
    def _trace(message, *args, **kwargs):
        if logging.getLogger().isEnabledFor(CustomLogLevel.TRACE.value):
            logging.log(CustomLogLevel.TRACE.value, message, *args, **kwargs)
    @staticmethod
    def append_to_logging():
        # add to logging module
        logging.low_trace = LoggingUtils._low_trace
        logging.base_trace = LoggingUtils._base_trace
        logging.trace = LoggingUtils._trace

        # Set up handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)

    @staticmethod
    def set_logging_level(log_level=logging.INFO):
        LoggingUtils.append_to_logging()
        logging.getLogger().setLevel(log_level) 
        logging.basicConfig(level=log_level)
