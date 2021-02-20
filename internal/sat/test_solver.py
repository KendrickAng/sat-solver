import unittest
from internal.sat.formula import Formula
from internal.sat.model import Model
from internal.sat.clause import Clause
from internal.sat.state_manager import StateManager, History, ImplicationGraphNode
from internal.sat.symbol import Symbol
from internal.sat.symbols import Symbols
from internal.sat.solver import Solver
from internal.sat.constants import TRUE, FALSE, UNASSIGNED
from internal.utils.logger import Logger
from collections import deque, defaultdict

class TestSolver(unittest.TestCase):
    def setUp(self):
        Logger.set_level("DEBUG")
        self.logger = Logger.get_logger()

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

    def test_unit_propagate(self):
        """
        https://www.slideshare.net/sakai/how-a-cdcl-sat-solver-works
        Input:
        Formula:    w1 (-1,-4,5), w2 (-4,6), w3 (-5,-6,7), w4 (-7,8), w5 (-2,-7,9), w6 (-8,-9), w7(-8,9)
        Model:      { 1:True, 2:True, 3:True, 4:True, rest unassigned }
        IG:         { 1:INode(1,True,1,None), 2:INode(2,True,2,None), 3:INode(3,True,3,None), 4:INode(4,True,4,None) }
        History:    { 1:deque([1]), 2:deque([2]), 3:deque([3]), 4:deque([4])}
        Output:     w6 (the conflicting clause)
        """
        # Create symbols
        x1 = Symbol("1", True)
        x2 = Symbol("2", True)
        x3 = Symbol("3", True)
        x4 = Symbol("4", True)
        x5 = Symbol("5", True)
        x6 = Symbol("6", True)
        x7 = Symbol("7", True)
        x8 = Symbol("8", True)
        x9 = Symbol("9", True)
        # Create clauses
        w1 = Clause([x1.negate(),x4.negate(),x5])
        w2 = Clause([x4.negate(),x6])
        w3 = Clause([x5.negate(),x6.negate(),x7])
        w4 = Clause([x7.negate(),x8])
        w5 = Clause([x2.negate(),x7.negate(),x9])
        w6 = Clause([x8.negate(),x9.negate()])
        w7 = Clause([x8.negate(),x9])
        # Create formula
        f = Formula([w1,w2,w3,w4,w5,w6,w7])
        # Lower level integration tests: model, symbols, history (no test for implication graph)
        m_actual = Model.from_symbols([x1,x2,x3,x4,x5,x6,x7,x8,x9])
        m_actual.extend(x1,TRUE)
        m_actual.extend(x2,TRUE)
        m_actual.extend(x3,TRUE)
        m_actual.extend(x4,TRUE)
        m_expected = Model.from_mapping({x1:TRUE,x1.negate():FALSE,
                                x2:TRUE,x2.negate():FALSE,
                                x3:TRUE,x3.negate():FALSE,
                                x4:TRUE,x4.negate():FALSE,
                                x5:UNASSIGNED,x5.negate():UNASSIGNED,
                                x6:UNASSIGNED,x6.negate():UNASSIGNED,
                                x7:UNASSIGNED,x7.negate():UNASSIGNED,
                                x8:UNASSIGNED,x8.negate():UNASSIGNED,
                                x9:UNASSIGNED,x9.negate():UNASSIGNED})
        self.assertEqual(m_actual, m_expected)
        sbls_expected = Symbols() # unassigned symbols
        sbls_expected.add(x5)
        sbls_expected.add(x6)
        sbls_expected.add(x7)
        sbls_expected.add(x8)
        sbls_expected.add(x9)
        sbls_actual = Symbols.from_values(deque([x5,x6,x7,x8,x9]))
        self.assertEqual(sbls_actual, sbls_expected)
        implication_graph = {
            x1: ImplicationGraphNode.from_values(x1, TRUE, 1, None, [], []),
            x2: ImplicationGraphNode.from_values(x2, TRUE, 2, None, [], []),
            x3: ImplicationGraphNode.from_values(x3, TRUE, 3, None, [], []),
            x4: ImplicationGraphNode.from_values(x4, TRUE, 4, None, [], []),
        }
        history_actual = History()
        history_actual.add_history(1, x1)
        history_actual.add_history(2, x2)
        history_actual.add_history(3, x3)
        history_actual.add_history(4, x4)
        history_expected = History.from_values(defaultdict(
            deque,
            {
                1: deque([x1]),
                2: deque([x2]),
                3: deque([x3]),
                4: deque([x4]),
            }
        ))
        self.assertEqual(history_actual, history_expected)
        # Higher level integration tests (using API from StateManager)
        sm_actual = StateManager(Symbols.from_values(deque([x1,x2,x3,x4,x5,x6,x7,x8,x9])))
        sm_actual.graph_add_node(x1,TRUE,None,1) # also updates history
        sm_actual.graph_add_node(x2,TRUE,None,2)
        sm_actual.graph_add_node(x3,TRUE,None,3)
        sm_actual.graph_add_node(x4,TRUE,None,4)
        sm_actual.sbls_mark_assigned(x1)
        sm_actual.sbls_mark_assigned(x2)
        sm_actual.sbls_mark_assigned(x3)
        sm_actual.sbls_mark_assigned(x4)
        sm_expected = StateManager.from_values(sbls_expected,implication_graph,history_expected)
        self.assertEqual(sm_actual, sm_expected)

        conf_clause = Solver.unit_propagate(f, m_actual, sm_actual, 4)
        self.assertEqual(conf_clause, w6)

        # EXTRA: test conflict analysis
        learnt_clause, bt_lvl = Solver.conflict_analysis(conf_clause, sm_actual, 4)
        self.assertEqual(learnt_clause, Clause([x2.negate(), x7.negate()]))
        self.assertEqual(bt_lvl, 2)

        # EXTRA: backtrack to level 2 with magic number 4 (current dl)
        l1 = len(sm_actual.unassigned_symbols)
        l2 = len(sm_actual.history.get_history_at_lvl(3))
        l3 = len(sm_actual.history.get_history_at_lvl(4))
        Solver.backtrack(sm_actual, bt_lvl, 4)
        l4 = len(sm_actual.unassigned_symbols)
        self.assertTrue(4 not in sm_actual.history)
        self.assertTrue(3 not in sm_actual.history)
        self.assertTrue(2 in sm_actual.history)
        self.assertTrue(l4 == l1 + l2 + l3)

    def test_pick_branching_variable(self):
        symbols = Symbols() # unassigned symbols
        x1 = Symbol("1", True)
        x2 = Symbol("2", True)
        x3 = Symbol("3", True)
        symbols.add(x1)
        symbols.add(x2)
        symbols.add(x3)
        implication_graph = {}
        history = History()
        sm = StateManager.from_values(symbols, implication_graph, history)
        sbl, val = Solver.pick_branching_variable_update_state(sm, 1)
        self.assertTrue(sbl == x1 or sbl == x2 or sbl == x3)
        self.assertTrue(val is TRUE or val is FALSE)
        # one symbol should have been removed from unassigned symbols
        self.assertTrue(len(sm.unassigned_symbols) == 2)
        # implication graph and history should be updated with branching variable
        self.assertTrue(len(sm.history) == 1)
        self.assertTrue(len(sm.implication_graph) == 1)

    def test_conflict_analysis(self):
        return True

    def test_backtrack(self):
        return True

    def test_resolution(self):
        """
        Resolution algorithm.
        [-7,-9] and [-2,-7,9] -> [-2,-7]
        [-7,-9] and [-2,8] -> Exception
        """
        x2 = Symbol("2", TRUE)
        x7 = Symbol("7", TRUE)
        x8 = Symbol("8", TRUE)
        x9 = Symbol("9", TRUE)
        c1 = Clause([x7.negate(),x9.negate()])
        c2 = Clause([x2.negate(),x7.negate(),x9])
        c3 = Clause([x2.negate(),x8])
        res1_actual = Solver.resolution(c1, c2, x9)
        res1_expected = Clause([x2.negate(),x7.negate()])
        # Normal resolution
        self.assertEqual(res1_actual, res1_expected)
        # Resolution with no common symbol
        self.assertRaises(Exception, Solver.resolution, c1, c3, x7)

    def test_to_positive(self):
        """
        Solver.to_positive(1, TRUE) -> (1, TRUE)
        Solver.to_positive(1, FALSE) -> (1, FALSE)
        Solver.to_positive(-1, TRUE) -> (1, FALSE)
        """
        s = Symbol("1", TRUE)
        self.assertEqual(Solver.to_positive(s, TRUE), (s, TRUE))
        self.assertEqual(Solver.to_positive(s, FALSE), (s, FALSE))
        self.assertEqual(Solver.to_positive(s.negate(), TRUE), (s, FALSE))
        return True
