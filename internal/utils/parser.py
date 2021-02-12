from internal.utils.logger import Logger
from internal.utils.exceptions import FileFormatError

logger = Logger.get_logger()

class Parser:
    def __init__(self):
        pass

    def parse(self, filepath: str):
        # TODO agree on interface, implement
        with open(filepath) as f:
            for line in f.readlines():
                if len(line) <= 0:
                    raise FileFormatError("No empty lines allowed")
                elif line[0] == 'c':
                    logger.info(line) # todo
                elif line[0] == 'p':
                    logger.info(line) # todo
                else:
                    logger.info(line) # todo
        return [], []
