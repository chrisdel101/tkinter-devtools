import logging

class LoggingUtils:
    # level consts
    TRACE = 8
    BASE_TRACE = 3
    LOW_TRACE = 5
    # define the new levels
    logging.addLevelName(BASE_TRACE, "base_trace")
    logging.addLevelName(LOW_TRACE, "low_trace")
    logging.addLevelName(TRACE, "trace")

    @staticmethod
    def _low_trace(message, *args, **kwargs):
        if logging.getLogger().isEnabledFor(LoggingUtils.LOW_TRACE):
            logging.log(LoggingUtils.LOW_TRACE, message, *args, **kwargs)
    @staticmethod
    def _base_trace(message, *args, **kwargs):
        if logging.getLogger().isEnabledFor(LoggingUtils.BASE_TRACE):
            logging.log(LoggingUtils.BASE_TRACE, message, *args, **kwargs)
    @staticmethod
    def _trace(message, *args, **kwargs):
        if logging.getLogger().isEnabledFor(LoggingUtils.TRACE):
            logging.log(LoggingUtils.TRACE, message, *args, **kwargs)

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
