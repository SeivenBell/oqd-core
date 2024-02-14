from typing import Any

########################################################################################

from quantumion.compiler.visitor import Transformer

from quantumion.interface.math import *

########################################################################################


class PrintMathExpr(Transformer):
    def _visit(self, model: Any):
        raise TypeError("Incompatible type for input model")

    def visit_MathVar(self, model: MathVar):
        string = "{}".format(model.name)
        return string

    def visit_MathNum(self, model: MathNum):
        string = "{}".format(model.value)
        return string

    def visit_MathImag(self, model: MathImag):
        string = "1j"
        return string

    def visit_MathUnary(self, model: MathUnary):
        string = "{}({})".format(model.func, self.visit(model.expr))
        return string

    def visit_MathAdd(self, model: MathAdd):
        string = "{} + {}".format(self.visit(model.expr1), self.visit(model.expr2))
        return string

    def visit_MathSub(self, model: MathSub):
        string = "{} - {}".format(self.visit(model.expr1), self.visit(model.expr2))
        return string

    def visit_MathMul(self, model: MathMul):
        s1 = (
            f"({self.visit(model.expr1)})"
            if isinstance(model.expr1, (MathAdd, MathSub))
            else self.visit(model.expr1)
        )
        s2 = (
            f"({self.visit(model.expr2)})"
            if isinstance(model.expr2, (MathAdd, MathSub))
            else self.visit(model.expr2)
        )

        string = "{} * {}".format(s1, s2)
        return string

    def visit_MathDiv(self, model: MathDiv):
        s1 = (
            f"({self.visit(model.expr1)})"
            if isinstance(model.expr1, (MathAdd, MathSub))
            else self.visit(model.expr1)
        )
        s2 = (
            f"({self.visit(model.expr2)})"
            if isinstance(model.expr2, (MathAdd, MathSub))
            else self.visit(model.expr2)
        )

        string = "{} / {}".format(s1, s2)
        return string

    def visit_MathPow(self, model: MathPow):
        s1 = (
            f"({self.visit(model.expr1)})"
            if isinstance(model.expr1, (MathAdd, MathSub, MathMul, MathDiv))
            else self.visit(model.expr1)
        )
        s2 = (
            f"({self.visit(model.expr2)})"
            if isinstance(model.expr2, (MathAdd, MathSub, MathMul, MathDiv))
            else self.visit(model.expr2)
        )

        string = "{}**{}".format(s1, s2)
        return string


########################################################################################


class ReorderMathExpr(Transformer):

    def visit_MathMul(self, model: MathMul):
        if isinstance(model.expr2, MathNum):
            return MathMul(expr1=self.visit(model.expr2), expr2=self.visit(model.expr1))
        return MathMul(expr1=self.visit(model.expr1), expr2=self.visit(model.expr2))

    def visit_MathAdd(self, model: MathAdd):
        if isinstance(model.expr2, MathNum):
            return MathAdd(expr1=self.visit(model.expr2), expr2=self.visit(model.expr1))
        return MathAdd(expr1=self.visit(model.expr1), expr2=self.visit(model.expr2))
