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
    Class representing the abstract syntax tree (AST) for a quantum operator
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
    """
    Class representing a terminal in the [`Operator`][quantumion.interface.analog.operator.Operator] abstract syntax tree (AST)
    """

    pass


########################################################################################


class Pauli(OperatorTerminal):
    """
    Class representing a Pauli operator
    """

    pass


class PauliI(Pauli):
    """
    Class for the Pauli I operator
    """

    pass


class PauliX(Pauli):
    """
    Class for the Pauli X operator
    """

    pass


class PauliY(Pauli):
    """
    Class for the Pauli Y operator
    """

    pass


class PauliZ(Pauli):
    """
    Class for the Pauli Z operator
    """

    pass


def PauliPlus():
    """
    Function that constructs the Pauli + operator
    """
    return OperatorAdd(
        op1=PauliX(),
        op2=OperatorScalarMul(
            op=PauliY(), expr=MathMul(expr1=MathImag(), expr2=MathNum(value=1))
        ),
    )


def PauliMinus():
    """
    Function that constructs the Pauli - operator
    """
    return OperatorAdd(
        op1=PauliX(),
        op2=OperatorScalarMul(
            op=PauliY(), expr=MathMul(expr1=MathImag(), expr2=MathNum(value=-1))
        ),
    )


########################################################################################


class Ladder(OperatorTerminal):
    """
    Class representing a ladder operator in Fock space
    """

    pass


class Creation(Ladder):
    """
    Class for the Creation operator in Fock space
    """

    pass


class Annihilation(Ladder):
    """
    Class for the Annihilation operator in Fock space
    """

    pass


class Identity(Ladder):
    """
    Class for the Identity operator in Fock space
    """

    pass


########################################################################################


class OperatorScalarMul(Operator):
    """
    Class representing scalar multiplication of an [`Operator`][quantumion.interface.analog.operator.Operator] and a
    [`MathExpr`][quantumion.interface.math.MathExpr]

    Attributes:
        op (Operator): [`Operator`][quantumion.interface.analog.operator.Operator] to multiply
        expr (MathExpr): [`MathExpr`][quantumion.interface.math.MathExpr] to multiply by
    """

    op: Operator
    expr: CastMathExpr


class OperatorBinaryOp(Operator):
    """
    Class representing binary operations on [`Operators`][quantumion.interface.analog.operator.Operator]
    """

    pass


class OperatorAdd(OperatorBinaryOp):
    """
    Class representing the addition of [`Operators`][quantumion.interface.analog.operator.Operator]

    Attributes:
        op1 (Operator): Left hand side [`Operator`][quantumion.interface.analog.operator.Operator]
        op2 (Operator): Right hand side [`Operator`][quantumion.interface.analog.operator.Operator]
    """

    op1: Operator
    op2: Operator


class OperatorSub(OperatorBinaryOp):
    """
    Class representing the subtraction of [`Operators`][quantumion.interface.analog.operator.Operator]

    Attributes:
        op1 (Operator): Left hand side [`Operator`][quantumion.interface.analog.operator.Operator]
        op2 (Operator): Right hand side [`Operator`][quantumion.interface.analog.operator.Operator]
    """

    op1: Operator
    op2: Operator


class OperatorMul(OperatorBinaryOp):
    """
    Class representing the multiplication of [`Operators`][quantumion.interface.analog.operator.Operator]

    Attributes:
        op1 (Operator): Left hand side [`Operator`][quantumion.interface.analog.operator.Operator]
        op2 (Operator): Right hand side [`Operator`][quantumion.interface.analog.operator.Operator]
    """

    op1: Operator
    op2: Operator


class OperatorKron(OperatorBinaryOp):
    """
    Class representing the tensor product of [`Operators`][quantumion.interface.analog.operator.Operator]

    Attributes:
        op1 (Operator): Left hand side [`Operator`][quantumion.interface.analog.operator.Operator]
        op2 (Operator): Right hand side [`Operator`][quantumion.interface.analog.operator.Operator]
    """

    op1: Operator
    op2: Operator
