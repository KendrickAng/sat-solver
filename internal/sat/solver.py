from internal.sat.model import Model
from internal.sat.symbols import Symbols
from internal.sat.formula import Formula
from internal.sat.constants import UNSAT, CONFLICT, SAT
from internal.utils.logger import Logger

logger = Logger.get_logger()

class Solver:
    def __init__(self, symbols: Symbols, formula: Formula, model: Model):
        self.symbols = symbols
        self.formula = formula
        self.model = model
        self.conflict = None

    # TODO complete algorithm
    def cdcl(self):
        up_result = self.unit_propagate(self.formula, self.model)
        if up_result == CONFLICT:
            return UNSAT
        dl = 0 # decision level
        while not self.all_variables_assigned(self.formula, self.model):

            # decide stage
            var, val = self.pick_branching_variable(self.formula, self.model)
            dl += 1
            self.model.extend(var, val)

            # deduce stage
            up_result = self.unit_propagate(self.formula, self.model)

            # diagnose stage
            if up_result == CONFLICT:
                lvl, learnt = self.conflict_analysis(self.formula, self.model)
                if lvl < 0:
                    return UNSAT
                else:
                    self.backtrack(self.formula, self.model, lvl)
                    # decrement decision level due to backtracking
                    dl = lvl
        return SAT