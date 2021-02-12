import logging
from internal.utils.exceptions import ArgumentFormatError

class Logger:
    """
    Program-wide logger. Instances of Logger should be created using the class methods withLevel.
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
        raise ArgumentFormatError(f"{level} is not a valid log level")

    @classmethod
    def get_logger(cls) -> logging.Logger:
        return logging.getLogger()
