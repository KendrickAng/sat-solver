import logging
from internal.utils.exceptions import ArgumentFormatError

# Add our own logging levels
logging.TRACE = 5
logging.addLevelName(logging.TRACE, "TRACE")

def trace(self, message, *args, **kws):
    if self.isEnabledFor(logging.TRACE):
        self._log(logging.TRACE, '\t{}'.format(message), args, **kws)

logging.Logger.trace = trace

class Logger:
    """
    Program-wide logger.
    """

    @classmethod
    def set_level(cls, level) -> None:
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(funcName)s][%(levelname)s]: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if level is None or level == "INFO":
            logger.setLevel(logging.INFO)
            return
        elif level == "DEBUG":
            logger.setLevel(logging.DEBUG)
            return
        elif level == "ERROR":
            logger.setLevel(logging.ERROR)
            return
        elif level == "TRACE":
            logger.setLevel(logging.TRACE)
            return
        elif level == "NONE":
            # turn off the logger
            logger.disabled = True
            return
        raise ArgumentFormatError(f"{level} is not a valid log level")

    @classmethod
    def get_logger(cls) -> logging.Logger:
        return logging.getLogger()
