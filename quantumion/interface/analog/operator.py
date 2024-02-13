from quantumion.interface.base import TypeReflectBaseModel
from quantumion.interface.math import CastMathExpr, MathExpr

########################################################################################

__all__ = [
    "Operator",
    "PauliI",
    "PauliX",
    "PauliY",
    "PauliZ",
    "Creation",
    "Annihilation",
    "Identity",
]


########################################################################################


class Operator(TypeReflectBaseModel):
    def __neg__(self):
        return OpNeg(op=self)

    def __add__(self, other):
        return OpAdd(op1=self, op2=other)

    def __sub__(self, other):
        return OpSub(op1=self, op2=other)

    def __matmul__(self, other):
        return OpKron(op1=self, op2=other)

    def __mul__(self, other):
        if isinstance(other, Operator):
            return OpMul(op1=self, op2=other)
        else:
            return OpScalarMul(op=self, expr=other)

    def __rmul__(self, other):
        return other * self

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


class OpNeg(Operator):
    op: Operator


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


########################################################################################

from typing import Any

from quantumion.compiler.visitor import Transform
from quantumion.compiler.math import PrintMathExpr


class PrintOperator(Transform):
    def _visit(self, model: Any):
        if isinstance(model, (Pauli, Ladder)):
            return model.class_ + "()"
        if isinstance(model, MathExpr):
            return model.accept(PrintMathExpr())
        raise TypeError("Incompatible type for input model")

    def visit_OpNeg(self, model: OpNeg):
        if not isinstance(model.op, (OpAdd, OpSub, OpMul)):
            string = "-{}".format(self.visit(model.op))
        else:
            string = "-({})".format(self.visit(model.op))
        return string

    def visit_OpAdd(self, model: OpAdd):
        string = "{} + {}".format(self.visit(model.op1), self.visit(model.op2))
        return string

    def visit_OpSub(self, model: OpSub):
        string = "{} - {}".format(self.visit(model.op1), self.visit(model.op2))
        return string

    def visit_OpMul(self, model: OpMul):
        s1 = (
            f"({self.visit(model.op1)})"
            if isinstance(model.op1, (OpAdd, OpSub, OpKron))
            else self.visit(model.op1)
        )
        s2 = (
            f"({self.visit(model.op2)})"
            if isinstance(model.op2, (OpAdd, OpSub, OpKron))
            else self.visit(model.op2)
        )

        string = "{} * {}".format(s1, s2)
        return string

    def visit_OpKron(self, model: OpKron):
        s1 = (
            f"({self.visit(model.op1)})"
            if isinstance(model.op1, (OpAdd, OpSub))
            else self.visit(model.op1)
        )
        s2 = (
            f"({self.visit(model.op2)})"
            if isinstance(model.op2, (OpAdd, OpSub))
            else self.visit(model.op2)
        )

        string = "{} @ {}".format(s1, s2)
        return string

    def visit_OpScalarMul(self, model: OpScalarMul):
        s1 = (
            f"({self.visit(model.op)})"
            if isinstance(model.op, (OpAdd, OpSub))
            else self.visit(model.op)
        )
        s2 = self.visit(model.expr)

        string = "{} * {}".format(s1, s2)
        return string


########################################################################################

if __name__ == "__main__":
    pass
