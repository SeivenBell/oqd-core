from quantumion.interface.base import TypeReflectBaseModel
from quantumion.interface.math import CastMathExpr, MathExpr, MathImag, MathNum, MathMul

########################################################################################

__all__ = [
    "Operator",
    "OperatorTerminal",
    "Pauli",
    "PauliI",
    "PauliX",
    "PauliY",
    "PauliZ",
    "PauliPlus",
    "PauliMinus",
    "Ladder",
    "Creation",
    "Annihilation",
    "Identity",
    "OperatorBinaryOp",
    "OperatorAdd",
    "OperatorSub",
    "OperatorMul",
    "OperatorScalarMul",
    "OperatorKron",
]


########################################################################################


class Operator(TypeReflectBaseModel):
    """
    Class representing a quantum operator
    """

    def __neg__(self):
        return OperatorScalarMul(op=self, expr=MathNum(value=-1))

    def __pos__(self):
        return self

    def __add__(self, other):
        return OperatorAdd(op1=self, op2=other)

    def __sub__(self, other):
        return OperatorSub(op1=self, op2=other)

    def __matmul__(self, other):
        if isinstance(other, MathExpr):
            raise TypeError(
                "Tried Kron product between Operator and MathExpr. "
                + "Scalar multiplication of MathExpr and Operator should be bracketed when perfoming Kron product."
            )
        return OperatorKron(op1=self, op2=other)

    def __mul__(self, other):
        if isinstance(other, Operator):
            return OperatorMul(op1=self, op2=other)
        else:
            return OperatorScalarMul(op=self, expr=other)

    def __rmul__(self, other):
        other = MathExpr.cast(other)
        return self * other

    pass


########################################################################################


class OperatorTerminal(Operator):
    pass


########################################################################################


class Pauli(OperatorTerminal):
    pass


class PauliI(Pauli):
    pass


class PauliX(Pauli):
    pass


class PauliY(Pauli):
    pass


class PauliZ(Pauli):
    pass


def PauliPlus():
    return OperatorAdd(
        op1=PauliX(),
        op2=OperatorScalarMul(
            op=PauliY(), expr=MathMul(expr1=MathImag(), expr2=MathNum(value=1))
        ),
    )


def PauliMinus():
    return OperatorAdd(
        op1=PauliX(),
        op2=OperatorScalarMul(
            op=PauliY(), expr=MathMul(expr1=MathImag(), expr2=MathNum(value=-1))
        ),
    )


########################################################################################


class Ladder(OperatorTerminal):
    pass


class Creation(Ladder):
    pass


class Annihilation(Ladder):
    pass


class Identity(Ladder):
    pass


########################################################################################


class OperatorScalarMul(Operator):
    op: Operator
    expr: CastMathExpr


class OperatorBinaryOp(Operator):
    pass


class OperatorAdd(OperatorBinaryOp):
    op1: Operator
    op2: Operator


class OperatorSub(OperatorBinaryOp):
    op1: Operator
    op2: Operator


class OperatorMul(OperatorBinaryOp):
    op1: Operator
    op2: Operator


class OperatorKron(OperatorBinaryOp):
    op1: Operator
    op2: Operator
