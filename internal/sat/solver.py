from typing import List
from internal.sat.model import Model
from internal.sat.symbols import Symbols
from internal.sat.clause import Clause
from internal.utils.logger import Logger

logger = Logger.get_logger()

class Solver:
    def __init__(self, symbols: Symbols, clauses: List[Clause], model: Model):
        self.sbls = symbols
        self.cls = clauses
        self.mdl = model

    # TODO complete algorithm
    def cdcl(self):
        logger.info(f"Symbols: {self.sbls}")
        logger.info(f"Clauses: {self.cls}")
        logger.info("Solving!")

