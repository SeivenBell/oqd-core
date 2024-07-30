from typing import Any, Union

########################################################################################

from quantumion.interface.analog import *
from quantumion.interface.math import MathExpr
from quantumion.compilerv2.rule import *
from quantumion.compilerv2.walk import *
from quantumion.compilerv2.math.utils import PrintMathExpr, VerbosePrintMathExpr


class PrintOperator(ConversionRule):

    def map_OperatorTerminal(self, model: OperatorTerminal, operands):
        return model.class_ + "()"

    def map_MathExpr(self, model: MathExpr, operands):
        return PostConversion(PrintMathExpr())(model)

    def map_OperatorAdd(self, model: OperatorAdd, operands):
        string = "{} + {}".format(operands['op1'], operands['op2'])
        return string

    def map_OperatorSub(self, model: OperatorSub, operands):
        s2 = (
            f"({operands['op2']})"
            if isinstance(model.op2, (OperatorAdd, OperatorSub))
            else operands['op2']
        )
        string = "{} - {}".format(operands['op1'], s2)
        return string

    def map_OperatorMul(self, model: OperatorMul, operands):
        s1 = (
            f"({operands['op1']})"
            if isinstance(
                model.op1, (OperatorAdd, OperatorSub, OperatorKron, OperatorScalarMul)
            )
            else operands['op1']
        )
        s2 = (
            f"({operands['op2']})"
            if isinstance(
                model.op2, (OperatorAdd, OperatorSub, OperatorKron, OperatorScalarMul)
            )
            else operands['op2']
        )
        string = "{} * {}".format(s1, s2)
        return string

    def map_OperatorKron(self, model: OperatorKron, operands):
        s1 = (
            f"({operands['op1']})"
            if isinstance(
                model.op1, (OperatorAdd, OperatorSub, OperatorMul, OperatorScalarMul)
            )
            else operands['op1']
        )
        s2 = (
            f"({operands['op2']})"
            if isinstance(
                model.op2, (OperatorAdd, OperatorSub, OperatorMul, OperatorScalarMul)
            )
            else operands['op2']
        )

        string = "{} @ {}".format(s1, s2)
        return string

    def map_OperatorScalarMul(self, model: OperatorScalarMul, operands):
        s1 = (
            f"({operands['op']})"
            if isinstance(
                model.op, (OperatorAdd, OperatorSub, OperatorMul, OperatorKron)
            )
            else operands['op']
        )
        s2 = f"({operands['expr']})"

        string = "{} * {}".format(s2, s1)
        return string
    
class VerbosePrintOperator(PrintOperator):
    def map_MathExpr(self, model: MathExpr, operands):
        return PostConversion(VerbosePrintMathExpr())(model)

    def _OperatorBinaryOp(self, model: OperatorBinaryOp, operands):
        s1 = (
            f"({operands['op1']})"
            if not isinstance(model.op1, OperatorTerminal)
            else operands['op1']
        )
        s2 = (
            f"({operands['op2']})"
            if not isinstance(model.op2, OperatorTerminal)
            else operands['op2']
        )
        string = "{} {} {}".format(
            s1,
            dict(OperatorAdd="+", OperatorSub="-", OperatorMul="*", OperatorKron="@")[
                model.__class__.__name__
            ],
            s2,
        )
        return string

    def map_OperatorAdd(self, model: OperatorAdd, operands):
        return self._OperatorBinaryOp(model, operands)

    def map_OperatorSub(self, model: OperatorSub, operands):
        return self._OperatorBinaryOp(model, operands)

    def map_OperatorMul(self, model: OperatorMul, operands):
        return self._OperatorBinaryOp(model, operands)

    def map_OperatorKron(self, model: OperatorKron, operands):
        return self._OperatorBinaryOp(model, operands)

    def map_OperatorScalarMul(self, model: OperatorScalarMul, operands):
        s1 = (
            f"({operands['op']})"
            if not isinstance(model.op, OperatorTerminal)
            else operands['op']
        )
        s2 = f"({operands['expr']})"

        string = "{} * {}".format(s2, s1)
        return string
    
def _get_index(model):
    if isinstance(model, Pauli):
        return (1,0)
    if isinstance(model, Union[Ladder, OperatorMul]):
        return (0,1)

def _sum_tuple(tuple1, tuple2):
    return  tuple(map(sum, zip(tuple1, tuple2)))

def get_canonical_hamiltonian_dim(model):
    """
    Note that we do not need to traverse through the whole tree to get this information an thus doing this through analysis seems like an overkill
    """
    dim = (0,0)
    if isinstance(model, OperatorAdd):
        model = model.op2
    if isinstance(model.op, OperatorKron):
        kron_model = model.op
        while isinstance(kron_model, OperatorKron):
            dim = _sum_tuple(dim, _get_index(kron_model.op2))
            kron_model = kron_model.op1

        dim = dim = _sum_tuple(dim, _get_index(kron_model))
        return dim
    dim = _get_index(model.op)
    return dim

if __name__ == '__main__':
    from quantumion.compiler.analog.base import PauliX, PauliY, PauliZ, PauliI, Annihilation, Creation, Identity
    X, Y, Z, I, A, C, LI = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()
    exp = X@Y + (3*(Y)*4)*(Y@Z@Y@Y)
    # exp = AnalogGate(hamiltonian=(X+Y+Z)) # applying VPO on this doesnn't make sense as we can't have str in hamiltonian field
    pprint(PostConversion(VerbosePrintOperator())(exp))
