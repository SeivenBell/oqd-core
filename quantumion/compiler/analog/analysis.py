from quantumion.interface.analog import *
from quantumion.compiler.walk import In
from quantumion.compiler.rule import RewriteRule
from typing import Union


class TermIndex(RewriteRule):
    """
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli, NormalOrder
    (without NormalOrder, TermIndex is not useful. For example, TermIndex of A*C and C*A is the same (2,1).
    Hence, NormalOrder is a requirement.
    """
    def __init__(self):
        super().__init__()
        self.term_idx = [[]]
        self._potential_terminal = True
    def _get_index(self, model):
        if isinstance(model, PauliI):
            return 0
        if isinstance(model, PauliX):
            return 1
        if isinstance(model, PauliY):
            return 2
        if isinstance(model, PauliZ):
            return 3
        if isinstance(model, Annihilation):
            return (1, 0)
        if isinstance(model, Creation):
            return (1, 1)
        if isinstance(model, Identity):
            return (0, 0)
    def map_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op1, Union[OperatorTerminal, OperatorMul]):
            if self._potential_terminal:
                self.term_idx[-1] = []

        if isinstance(model.op1, Union[OperatorTerminal]):

            self.term_idx[-1].insert(0, self._get_index(model.op1))
            self.term_idx[-1].insert(1, self._get_index(model.op2))
        elif not isinstance(model.op2, OperatorMul):
            self.term_idx[-1].insert(len(self.term_idx[-1]), self._get_index(model.op2))

    def map_OperatorTerminal(self, model):
        if self.term_idx[-1] == []:
            self.term_idx[-1] = [self._get_index(model=model)]
            self._potential_terminal = True
        else:
            self._potential_terminal = False
        

    def map_OperatorAdd(self, model: OperatorAdd):
        self.term_idx.append([])

    def map_OperatorMul(self, model):

        if isinstance(model.op1, Ladder) and isinstance(model.op2, Ladder):
            if self._potential_terminal:
                self.term_idx[-1] = []
            
            term1 = self._get_index(model.op1)
            term2 = self._get_index(model.op2)
            self.term_idx[-1].insert(len(self.term_idx[-1]), (term1[0]+term2[0], term1[1]+term2[1]))
        else:
            idx = len(self.term_idx[-1]) - 1
            new = self._get_index(model.op2)
            self.term_idx[-1][idx] =  (self.term_idx[-1][idx][0]+new[0], self.term_idx[-1][idx][1]+new[1])
