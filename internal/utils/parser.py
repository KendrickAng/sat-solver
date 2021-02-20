from typing import List
from internal.utils.logger import Logger
from internal.utils.exceptions import FileFormatError
from internal.sat.clause import Clause
from internal.sat.symbol import Symbol
from internal.sat.symbols import Symbols
from internal.sat.formula import Formula

logger = Logger.get_logger()

class Parser:
    def __init__(self):
        pass

    def parse(self, filepath: str) -> (Symbols, Formula):
        """
        Returns symbols parsed IN THE FILE and the clause list.
        """
        with open(filepath) as f:
            num_variables = -1
            num_clauses = -1
            # Read comments and variable/clause number dec
            line = f.readline().strip()
            while line:
                if len(line) <= 0:
                    raise FileFormatError("No empty lines allowed")
                elif line[0] == 'c':
                    pass # don't process comments
                elif line[0] == 'p':
                    tokens = line.split()
                    if len(tokens) != 4:
                        raise FileFormatError("Incorrect declaration for clauses")
                    num_variables = int(tokens[2])
                    num_clauses = int(tokens[3])

                    if num_variables == -1 and num_clauses == -1:
                        raise FileFormatError("Clause declaration before variable/clause number declaration")
                    # Read clauses and variables
                    clauses = []
                    symbols = Symbols()
                    for _ in range(num_clauses):
                        tokens = f.readline().strip().split()
                        if tokens[-1] != '0':
                            raise FileFormatError("Clause declaration must end with 0")
                        sbl_lst = list(map(self.parse_symbol, tokens[:-1]))
                        clauses.append(Clause(sbl_lst))
                        # Add read symbols as we go
                        for s in sbl_lst:
                            symbols.add(s.to_positive()) # changing it to positive shouldn't affect anything
                    return symbols, Formula(clauses)

                line = f.readline().strip()
        raise FileFormatError("You should not be here")

    def parse_symbol(self, sbl: str):
        if sbl and sbl[0] == '-' and sbl[1:].isalnum():
            return Symbol(sbl[1:], False)
        elif sbl.isalnum():
            return Symbol(sbl, True)
        raise FileFormatError(f"Wrong symbol syntax {sbl}")
