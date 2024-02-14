from quantumion.interface.base import TypeReflectBaseModel
from quantumion.interface.math import CastMathExpr, MathExpr

########################################################################################

__all__ = [
    "Operator",
    "Pauli",
    "PauliI",
    "PauliX",
    "PauliY",
    "PauliZ",
    "Ladder",
    "Creation",
    "Annihilation",
    "Identity",
    "OpAdd",
    "OpSub",
    "OpMul",
    "OpScalarMul",
    "OpKron",
]


########################################################################################


class Operator(TypeReflectBaseModel):
    def __neg__(self):
        return OpScalarMul(op=self, expr=MathExpr.cast(-1))

    def __pos__(self):
        return self

    def __add__(self, other):
        return OpAdd(op1=self, op2=other)

    def __sub__(self, other):
        return OpSub(op1=self, op2=other)

    def __matmul__(self, other):
        if isinstance(other, MathExpr):
            raise TypeError(
                "Tried Kron product between Operator and MathExpr. "
                + "Scalar multiplication of MathExpr and Operator should be bracketed when perfoming Kron product."
            )
        return OpKron(op1=self, op2=other)

    def __mul__(self, other):
        if isinstance(other, Operator):
            return OpMul(op1=self, op2=other)
        else:
            return OpScalarMul(op=self, expr=other)

    def __rmul__(self, other):
        other = MathExpr.cast(other)
        return self * other

    pass


########################################################################################


class Pauli(Operator):
    pass


class PauliI(Pauli):
    pass


class PauliX(Pauli):
    pass


class PauliY(Pauli):
    pass


class PauliZ(Pauli):
    pass


########################################################################################


class Ladder(Operator):
    pass


class Creation(Ladder):
    pass


class Annihilation(Ladder):
    pass


class Identity(Ladder):
    pass


########################################################################################


class OpScalarMul(Operator):
    op: Operator
    expr: CastMathExpr


class OpAdd(Operator):
    op1: Operator
    op2: Operator


class OpSub(Operator):
    op1: Operator
    op2: Operator


class OpMul(Operator):
    op1: Operator
    op2: Operator


class OpKron(Operator):
    op1: Operator
    op2: Operator
