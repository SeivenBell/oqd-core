from typing import Any

########################################################################################

from quantumion.compiler.visitor import Transform

from quantumion.interface.math import (
    MathVar,
    MathNum,
    MathImag,
    MathAdd,
    MathSub,
    MathMul,
    MathDiv,
    MathPow,
    MathUnary,
)

########################################################################################


class PrintMathExpr(Transform):
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
