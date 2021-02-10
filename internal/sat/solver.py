from typing import List
from internal.sat.model import Model

class Solver:
    def __init__(self, symbols: List[str], clauses: List[str], model: Model):
        self.sbls = symbols
        self.cls = clauses
        self.mdl = model

    # TODO complete algorithm
    def cdcl(self):
        print("Solved the problem!")

