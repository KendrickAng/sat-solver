from internal.sat.symbol import Symbol
from internal.sat.clause import Clause

class ImplicationGraph:
    """
    During execution of CDCL, assigned variables as well as their antecedents define a directed acyclic graph.
    This is called an Implication Graph.
    """
    def __init__(self):
        # TODO Implement this, don't forget that node symbols can be negative due to my implementation
        self.graph = {}

    def add_vertex(self, s: Symbol, val: bool, antecedent: Clause, dl: int):
        pass
        # assert s not in self.adj_list
        # assert s.neg() not in self.adj_list
        # self.graph[s] =

class ImplicationGraphNode:
    def __init__(self, s: Symbol, val: bool, dl: int):
        self.symbol = s
        self.value = val
        self.level = dl
