from typing import Any

########################################################################################

from quantumion.interface.analog import *
from quantumion.interface.math import MathExpr

from quantumion.compiler.visitor import Visitor, Transformer
from quantumion.compiler.math import PrintMathExpr, VerbosePrintMathExpr

from quantumion.utils.color import random_hexcolor

########################################################################################

__all__ = [
    "AnalogCircuitVisitor",
    "AnalogCircuitTransformer",
    "PrintOperator",
    "VerbosePrintOperator",
    "MermaidOperator",
]


########################################################################################


class AnalogCircuitVisitor(Visitor):
    pass


class AnalogCircuitTransformer(Transformer):
    pass


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


########################################################################################


class MermaidOperator(Transformer):

    def emit(self, model):
        self.element = 0

        self.mermaid_string = "```mermaid\ngraph TD\n"
        model.accept(self)
        self.mermaid_string += "".join(
            [
                f"classDef {model} stroke:{random_hexcolor()},stroke-width:3px\n"
                for model in [
                    "Pauli",
                    "Ladder",
                    "OperatorAdd",
                    "OperatorScalarMul",
                    "OperatorKron",
                    "OperatorMul",
                    "MathExpr",
                ]
            ]
        )
        self.mermaid_string += "```\n"

        return self.mermaid_string

    def visit_MathExpr(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}<br/>{}<br/>{}"):::{}\n'.format(
            self.element,
            "MathExpr",
            "-" * len("MathExpr"),
            "expr = #quot;{}#quot;".format(model.accept(PrintMathExpr())),
            "MathExpr",
        )
        self.element += 1

        return f"element{element}"

    def visit_Pauli(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element, model.__class__.__name__, "Pauli"
        )
        self.element += 1

        return f"element{element}"

    def visit_Ladder(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element, model.__class__.__name__, "Ladder"
        )
        self.element += 1

        return f"element{element}"

    def visit_OperatorBinaryOp(self, model):
        left = self.visit(model.op1)
        right = self.visit(model.op2)

        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            model.__class__.__name__,
        )

        self.mermaid_string += f"element{element} --> {left} & {right}\n"

        self.element += 1

        return f"element{element}"

    def visit_OperatorScalarMul(self, model):
        expr = self.visit(model.expr)
        op = self.visit(model.op)

        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            model.__class__.__name__,
        )

        self.mermaid_string += f"element{element} --> {expr} & {op}\n"

        self.element += 1

        return f"element{element}"
