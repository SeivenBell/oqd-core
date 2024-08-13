from typing import Any, Union

########################################################################################

from quantumion.interface.analog import *
from quantumion.interface.math import MathExpr
from quantumion.compiler.rule import ConversionRule
from quantumion.compiler.walk import Post
from quantumion.compiler.math.rules import PrintMathExpr

########################################################################################

__all__ = [
    "PrintOperator",
]

########################################################################################


class PrintOperator(ConversionRule):
    def __init__(self, *, verbose=False):
        super().__init__()
        self.verbose = verbose

    def map_OperatorTerminal(self, model: OperatorTerminal, operands):
        return model.class_ + "()"

    def map_MathExpr(self, model: MathExpr, operands):
        return Post(PrintMathExpr(verbose=self.verbose))(model)

    def map_OperatorAdd(self, model: OperatorAdd, operands):
        if self.verbose:
            return self._map_OperatorBinaryOp(model, operands)
        string = "{} + {}".format(operands["op1"], operands["op2"])
        return string

    def map_OperatorSub(self, model: OperatorSub, operands):
        if self.verbose:
            return self._map_OperatorBinaryOp(model, operands)
        s2 = (
            f"({operands['op2']})"
            if isinstance(model.op2, (OperatorAdd, OperatorSub))
            else operands["op2"]
        )
        string = "{} - {}".format(operands["op1"], s2)
        return string

    def map_OperatorMul(self, model: OperatorMul, operands):
        if self.verbose:
            return self._map_OperatorBinaryOp(model, operands)
        s1 = (
            f"({operands['op1']})"
            if isinstance(
                model.op1, (OperatorAdd, OperatorSub, OperatorKron, OperatorScalarMul)
            )
            else operands["op1"]
        )
        s2 = (
            f"({operands['op2']})"
            if isinstance(
                model.op2, (OperatorAdd, OperatorSub, OperatorKron, OperatorScalarMul)
            )
            else operands["op2"]
        )
        string = "{} * {}".format(s1, s2)
        return string

    def map_OperatorKron(self, model: OperatorKron, operands):
        if self.verbose:
            return self._map_OperatorBinaryOp(model, operands)
        s1 = (
            f"({operands['op1']})"
            if isinstance(
                model.op1, (OperatorAdd, OperatorSub, OperatorMul, OperatorScalarMul)
            )
            else operands["op1"]
        )
        s2 = (
            f"({operands['op2']})"
            if isinstance(
                model.op2, (OperatorAdd, OperatorSub, OperatorMul, OperatorScalarMul)
            )
            else operands["op2"]
        )

        string = "{} @ {}".format(s1, s2)
        return string

    def map_OperatorScalarMul(self, model: OperatorScalarMul, operands):
        if self.verbose:
            s1 = (
                f"({operands['op']})"
                if not isinstance(model.op, OperatorTerminal)
                else operands["op"]
            )
            s2 = f"({operands['expr']})"
            string = f"{s2} * {s1}"
            return string
        s1 = (
            f"({operands['op']})"
            if isinstance(
                model.op, (OperatorAdd, OperatorSub, OperatorMul, OperatorKron)
            )
            else operands["op"]
        )
        s2 = f"({operands['expr']})"

        string = f"{s2} * {s1}"
        return string

    def _map_OperatorBinaryOp(self, model: OperatorBinaryOp, operands):
        s1 = (
            f"({operands['op1']})"
            if not isinstance(model.op1, OperatorTerminal)
            else operands["op1"]
        )
        s2 = (
            f"({operands['op2']})"
            if not isinstance(model.op2, OperatorTerminal)
            else operands["op2"]
        )
        operator_dict = dict(
            OperatorAdd="+", OperatorSub="-", OperatorMul="*", OperatorKron="@"
        )
        string = f"{s1} {operator_dict[model.__class__.__name__]} {s2}"
        return string


########################################################################################q


def _get_index(model):
    if isinstance(model, Pauli):
        return (1, 0)
    if isinstance(model, Union[Ladder, OperatorMul]):
        return (0, 1)


def _sum_tuple(tuple1, tuple2):
    return tuple(map(sum, zip(tuple1, tuple2)))


def get_canonical_hamiltonian_dim(model):
    """
    Note that we do not need to traverse through the whole tree to get this information an thus doing this through analysis seems like an overkill
    """
    dim = (0, 0)
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


def term_index_dim(lst):
    if isinstance(lst, int):
        return [1, 0]
    if isinstance(lst, tuple):
        return [0, 1]
    dim = [0, 0]
    for elem in lst:
        if isinstance(elem, tuple):
            dim[1] = dim[1] + 1
        else:
            dim[0] = dim[0] + 1
    return dim
