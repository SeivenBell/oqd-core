from quantumion.compilerv2.base import PassBase
from quantumion.compilerv2.generic import *
from quantumion.compilerv2.rule import *
from quantumion.compilerv2.walk import *
from rich import print as pprint
from quantumion.interface.analog import *

from quantumion.compiler.analog.base import *

# expr = {'a': 0, 'b': 2}
out = Single(Chain(Pre(AddN(4)), Pre(AddOne()), Pre(AddOne()), Pre(AddOne())))
# pprint(out)
I, X, Z, Y = PauliI(), PauliX(), PauliZ(), PauliY()
op = Z @ (I*I)
# op = Creation() * Annihilation() * Identity()
out = Pre(CanVerPauliAlgebra())(op)
pprint(out)
# out = Pre(rule=AddOne())(model = expr)
# out = Pre(rule = AddOne())(expr)
# out = Chain(Pre(AddOne()))(expr)
# out = Pre(Chain(AddOne(), AddOne()))(expr)
def pass_tree(compiler: PassBase, level=0, *, print_fn=print):
    print_fn("  " * level + "- ", compiler, sep="")
    for c in compiler.children:
        pass_tree(c, level=level + 1, print_fn=print_fn)
    pass

# pass_tree(out, print_fn=pprint)


class CanVerPauliAlgebra(RewriteRule):
    """
    Assumptions:
    Distributed, Gathered and then proper ordered. Then MatMul is done on the set of operators.
    """

    def map_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, Pauli) and isinstance(model.op2, Pauli):
            raise CanonicalFormError("Incomplete Pauli Algebra")
        else:
            self.map(model.op1)
            self.map(model.op2)

    def map_VisitableBaseModel(self, model):
        pass

    def map_Operators(self,model):
        pass

class PruneIdentity(RewriteRule):
    """
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli, NormalOrder
    """

    def map_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, (Identity)):
            return self.map(model.op2)
        if isinstance(model.op2, (Identity)):
            return self.map(model.op1)
        pprint("model.op1 {}".format(model.op1))
        pprint("self {}".format(self.map))
        return OperatorMul(op1=self.map(model.op1), op2=self.map(model.op2))
    
    def map_Creation(self, model: Creation):
        return model
    
    def map_Annihilation(self, model: Annihilation):
        return model
    
    def map_Identity(self, model: Identity):
        return model