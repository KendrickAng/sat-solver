import unittest
from internal.sat.formula import Formula
from internal.sat.model import Model
from internal.sat.clause import Clause
from internal.sat.symbol import Symbol
from internal.sat.symbols import Symbols
from internal.sat.solver import Solver
from internal.sat.constants import TRUE, FALSE, UNASSIGNED

class TestSolver(unittest.TestCase):
    def test_all_variables_assigned(self):
        """
        [[1, 2], [3, 4]]
        {1: TRUE, 2: TRUE, 3: TRUE, 4: TRUE}
        > True
        """
        a = Symbol('a', TRUE)
        b = Symbol('b', TRUE)
        c = Symbol('c', TRUE)
        d = Symbol('d', TRUE)
        c1 = Clause([a, b])
        c2 = Clause([c, d])
        f = Formula([c1, c2])
        m_assigned = Model.from_mapping({a: TRUE, a.negate(): FALSE,
                                         b: TRUE, b.negate(): FALSE,
                                         c: TRUE, c.negate(): FALSE,
                                         d: TRUE, d.negate(): FALSE})
        m_unassigned = Model.from_mapping({a: TRUE, a.negate(): FALSE,
                                           b: TRUE, b.negate(): FALSE,
                                           c: UNASSIGNED, c.negate(): UNASSIGNED,
                                           d: TRUE, d.negate(): FALSE})
        self.assertEqual(Solver.all_variables_assigned(f, m_assigned), True, "all variables should be assigned")
        self.assertEqual(Solver.all_variables_assigned(f, m_unassigned), False, "there should be unassigned variables")


