from quantumion.interface.analog import *
from quantumion.compiler.walk import In
from quantumion.compiler.rule import RewriteRule
from typing import Union


class TestCase(RewriteRule):
    def map_Operator(self, model):
        pprint("test::: model is {}\n".format(model))
        return model

class TermIndexIn(RewriteRule):
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
        # if self._potential_terminal:
        #     self.term_idx = [[]]
        #     self._potential_terminal = False
        if isinstance(model.op1, Union[OperatorTerminal, OperatorMul]):
            if self._potential_terminal:
                self.term_idx[-1] = []
            # pprint(self.term_idx)
        if isinstance(model.op1, Union[OperatorTerminal]):

            self.term_idx[-1].insert(0, self._get_index(model.op1))
            self.term_idx[-1].insert(1, self._get_index(model.op2))
        elif not isinstance(model.op2, OperatorMul):
            self.term_idx[-1].insert(len(self.term_idx[-1]), self._get_index(model.op2))

    def map_OperatorTerminal(self, model):
        pprint("op terminal index is {}".format(self.term_idx))
        # if self.term_idx[-1] == [] and self._potential_terminal:
        #     self.term_idx[-1] = [self._get_index(model=model)]
        if self.term_idx[-1] == []:
            self.term_idx[-1] = [self._get_index(model=model)]
            self._potential_terminal = True
        else:
            self._potential_terminal = False
        pprint(self._potential_terminal)
        

    def map_OperatorAdd(self, model: OperatorAdd):
        # if isinstance(model.op1, OperatorAdd):

        self.term_idx.append([])

    def map_OperatorMul(self, model):
        # pprint("in opmul the term index is {}\n".format(self.term_idx))
        # pprint(model)
        # if self._potential_terminal:
        #     # self.term_idx = [[]]
        #     self.term_idx[-1] = []
        #     self._potential_terminal = False
        # pprint("in opmul after the term index is {}\n".format(self.term_idx))
        # pprint()
        if isinstance(model.op1, Ladder) and isinstance(model.op2, Ladder):
            if self._potential_terminal:
                self.term_idx[-1] = []
            
            # self.term_idx[-1].pop()
            term1 = self._get_index(model.op1)
            term2 = self._get_index(model.op2)
            self.term_idx[-1].insert(len(self.term_idx[-1]), (term1[0]+term2[0], term1[1]+term2[1]))
        else:
            # prev = self.term_idx[-1][len(self.term_idx[-1]]
            idx = len(self.term_idx[-1]) - 1
            new = self._get_index(model.op2)
            self.term_idx[-1][idx] =  (self.term_idx[-1][idx][0]+new[0], self.term_idx[-1][idx][1]+new[1])


A, C, J = Annihilation(), Creation(), Identity()
X, Y, Z, I = PauliX(), PauliY(), PauliZ(), PauliI()

from rich import print as pprint

op = (X@Y)+(Z@I@(C*A*C*A)) + 1*(Z@Y)
# op = A*C
op = A + C + A + (J*C*C) + C + X@X@(C*C*A)
# op = X@Y + Z@I + Y@I
# op = A*C*A
op = X@A@C@(A*C*C*A)@Z@I + A*C + X + (C*J*J*A)@(C*A)@(A*C)@A
compiler = In(TermIndexIn())
pprint("output is {}".format(compiler(op)))
pprint(compiler.children)