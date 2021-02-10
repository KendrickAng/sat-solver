from internal.utils.logger import Logger

logger = Logger.get_logger()

class Parser:

    def __init__(self):
        pass

    def parse(self, filepath: str):
        # TODO agree on interface, implement
        with open(filepath) as f:
            for line in f:
                logger.info(line)
        return [], []