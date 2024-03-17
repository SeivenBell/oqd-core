from typing import Any

########################################################################################

from quantumion.interface.analog import *
from quantumion.interface.math import MathExpr

from quantumion.compiler.visitor import Visitor, Transformer
from quantumion.compiler.math import PrintMathExpr, VerbosePrintMathExpr

########################################################################################

__all__ = [
    "AnalogCircuitVisitor",
    "AnalogCircuitTransformer",
    "AnalogCircuitIonsAnalysis",
    "PrintOperator",
    "VerbosePrintOperator",
    "AnalogInterfaceVisitor",
    "AnalogInterfaceTransformer",
]


########################################################################################


class AnalogCircuitVisitor(Visitor):
    pass


class AnalogCircuitTransformer(Transformer):
    pass

class AnalogInterfaceVisitor(Visitor):
    pass


class AnalogInterfaceTransformer(Transformer):
    pass

class AnalogCircuitIonsAnalysis(AnalogCircuitVisitor):
    def __init__(self):
        self.ions = 0

    def visit_AnalogCircuit(self, model: AnalogCircuit) -> None:
        assert isinstance(model, AnalogCircuit)
        self.ions = model.n_qreg


########################################################################################


class PrintOperator(AnalogCircuitTransformer):
    def _visit(self, model: Any):
        raise TypeError("Incompatible type for input model")

    def visit_OperatorTerminal(self, model: OperatorTerminal):
        return model.class_ + "()"

    def visit_MathExpr(self, model: MathExpr):
        return model.accept(PrintMathExpr())

    def visit_OperatorAdd(self, model: OperatorAdd):
        string = "{} + {}".format(self.visit(model.op1), self.visit(model.op2))
        return string

    def visit_OperatorSub(self, model: OperatorSub):
        s2 = (
            f"({self.visit(model.op2)})"
            if isinstance(model.op2, (OperatorAdd, OperatorSub))
            else self.visit(model.op2)
        )
        string = "{} - {}".format(self.visit(model.op1), s2)
        return string

    def visit_OperatorMul(self, model: OperatorMul):
        s1 = (
            f"({self.visit(model.op1)})"
            if isinstance(
                model.op1, (OperatorAdd, OperatorSub, OperatorKron, OperatorScalarMul)
            )
            else self.visit(model.op1)
        )
        s2 = (
            f"({self.visit(model.op2)})"
            if isinstance(
                model.op2, (OperatorAdd, OperatorSub, OperatorKron, OperatorScalarMul)
            )
            else self.visit(model.op2)
        )

        string = "{} * {}".format(s1, s2)
        return string

    def visit_OperatorKron(self, model: OperatorKron):
        s1 = (
            f"({self.visit(model.op1)})"
            if isinstance(
                model.op1, (OperatorAdd, OperatorSub, OperatorMul, OperatorScalarMul)
            )
            else self.visit(model.op1)
        )
        s2 = (
            f"({self.visit(model.op2)})"
            if isinstance(
                model.op2, (OperatorAdd, OperatorSub, OperatorMul, OperatorScalarMul)
            )
            else self.visit(model.op2)
        )

        string = "{} @ {}".format(s1, s2)
        return string

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        s1 = (
            f"({self.visit(model.op)})"
            if isinstance(
                model.op, (OperatorAdd, OperatorSub, OperatorMul, OperatorKron)
            )
            else self.visit(model.op)
        )
        s2 = f"({self.visit(model.expr)})"

        string = "{} * {}".format(s2, s1)
        return string


########################################################################################


class VerbosePrintOperator(PrintOperator):

    def visit_MathExpr(self, model: MathExpr):
        return model.accept(VerbosePrintMathExpr())

    def visit_OperatorBinaryOp(self, model: OperatorBinaryOp):
        s1 = (
            f"({self.visit(model.op1)})"
            if not isinstance(model.op1, OperatorTerminal)
            else self.visit(model.op1)
        )
        s2 = (
            f"({self.visit(model.op2)})"
            if not isinstance(model.op2, OperatorTerminal)
            else self.visit(model.op2)
        )
        string = "{} {} {}".format(
            s1,
            dict(OperatorAdd="+", OperatorSub="-", OperatorMul="*", OperatorKron="@")[
                model.__class__.__name__
            ],
            s2,
        )
        return string

    def visit_OperatorAdd(self, model: OperatorAdd):
        return self.visit_OperatorBinaryOp(model)

    def visit_OperatorSub(self, model: OperatorSub):
        return self.visit_OperatorBinaryOp(model)

    def visit_OperatorMul(self, model: OperatorMul):
        return self.visit_OperatorBinaryOp(model)

    def visit_OperatorKron(self, model: OperatorKron):
        return self.visit_OperatorBinaryOp(model)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        s1 = (
            f"({self.visit(model.op)})"
            if not isinstance(model.op, OperatorTerminal)
            else self.visit(model.op)
        )
        s2 = f"({self.visit(model.expr)})"

        string = "{} * {}".format(s2, s1)
        return string
