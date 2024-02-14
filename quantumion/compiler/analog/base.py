from typing import Any

########################################################################################

from quantumion.interface.analog import *
from quantumion.interface.math import MathExpr

from quantumion.compiler.visitor import Visitor, Transform
from quantumion.compiler.math import PrintMathExpr

########################################################################################


class AnalogCircuitVisitor(Visitor):
    pass


class AnalogCircuitTransform(Transform):
    pass


class AnalogCircuitIonsAnalysis(AnalogCircuitVisitor):
    def __init__(self):
        self.ions = 0

    def visit_AnalogCircuit(self, model: AnalogCircuit) -> None:
        assert isinstance(model, AnalogCircuit)
        self.ions = model.n_qreg


########################################################################################


class PrintOperator(AnalogCircuitTransform):
    def _visit(self, model: Any):
        if isinstance(model, (Pauli, Ladder)):
            return model.class_ + "()"
        if isinstance(model, MathExpr):
            return model.accept(PrintMathExpr())
        raise TypeError("Incompatible type for input model")

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
            if isinstance(model.op, (OpAdd, OpSub, OpKron))
            else self.visit(model.op)
        )
        s2 = f"({self.visit(model.expr)})"

        string = "{} * {}".format(s2, s1)
        return string
