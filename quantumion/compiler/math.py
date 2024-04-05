from typing import Any, Union

########################################################################################

from quantumion.interface.math import *

from quantumion.compiler.visitor import Transformer

from quantumion.utils.color import random_hexcolor

########################################################################################

__all__ = [
    "PrintMathExpr",
    "VerbosePrintMathExpr",
    "PartitionMathExpr",
    "DistributeMathExpr",
    "ProperOrderMathExpr",
    "MermaidMathExpr",
]

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

    def visit_MathFunc(self, model: MathFunc):
        string = "{}({})".format(model.func, self.visit(model.expr))
        return string

    def visit_MathAdd(self, model: MathAdd):
        string = "{} + {}".format(self.visit(model.expr1), self.visit(model.expr2))
        return string

    def visit_MathSub(self, model: MathSub):
        s2 = (
            f"({self.visit(model.expr2)})"
            if isinstance(model.expr2, (MathAdd, MathSub))
            else self.visit(model.expr2)
        )
        string = "{} - {}".format(self.visit(model.expr1), s2)
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

        string = "{} ** {}".format(s1, s2)
        return string


class VerbosePrintMathExpr(PrintMathExpr):
    def visit_MathBinaryOp(self, model: MathBinaryOp):
        s1 = (
            f"({self.visit(model.expr1)})"
            if not isinstance(model.expr1, (MathTerminal, MathUnaryOp))
            else self.visit(model.expr1)
        )
        s2 = (
            f"({self.visit(model.expr2)})"
            if not isinstance(model.expr2, (MathTerminal, MathUnaryOp))
            else self.visit(model.expr2)
        )
        string = "{} {} {}".format(
            s1,
            dict(MathAdd="+", MathSub="-", MathMul="*", MathDiv="/", MathPow="**")[
                model.__class__.__name__
            ],
            s2,
        )
        return string

    def visit_MathAdd(self, model: MathAdd):
        return self.visit_MathBinaryOp(model)

    def visit_MathSub(self, model: MathSub):
        return self.visit_MathBinaryOp(model)

    def visit_MathMul(self, model: MathMul):
        return self.visit_MathBinaryOp(model)

    def visit_MathDiv(self, model: MathDiv):
        return self.visit_MathBinaryOp(model)

    def visit_MathPow(self, model: MathPow):
        return self.visit_MathBinaryOp(model)


########################################################################################


class MermaidMathExpr(Transformer):

    def emit(self, model):
        self.element = 0

        self.mermaid_string = "```mermaid\ngraph TD\n"
        model.accept(self)
        self.mermaid_string += "".join(
            [
                f"classDef {model} stroke:{random_hexcolor()},stroke-width:3px\n"
                for model in [
                    "MathAdd",
                    "MathSub",
                    "MathMul",
                    "MathDiv",
                    "MathFunc",
                    "MathNum",
                    "MathVar",
                    "MathImag",
                ]
            ]
        )
        self.mermaid_string += "```\n"

        return self.mermaid_string

    def visit_MathImag(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            model.__class__.__name__,
        )
        self.element += 1

        return f"element{element}"

    def visit_MathVar(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}<br/>{}<br/>{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            "-" * len(model.__class__.__name__),
            "name = #quot;{}#quot;".format(model.name),
            model.__class__.__name__,
        )
        self.element += 1

        return f"element{element}"

    def visit_MathNum(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}<br/>{}<br/>{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            "-" * len(model.__class__.__name__),
            "value = {}".format(model.value),
            model.__class__.__name__,
        )
        self.element += 1

        return f"element{element}"

    def visit_MathBinaryOp(self, model):
        left = self.visit(model.expr1)
        right = self.visit(model.expr2)

        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            model.__class__.__name__,
        )

        self.mermaid_string += f"element{element} --> {left} & {right}\n"

        self.element += 1

        return f"element{element}"

    def visit_MathFunc(self, model):
        expr = self.visit(model.expr)

        element = self.element
        self.mermaid_string += 'element{}("{}<br/>{}<br/>{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            "-" * len(model.__class__.__name__),
            "func = {}".format(model.func),
            model.__class__.__name__,
        )

        self.mermaid_string += f"element{element} --> {expr}\n"

        self.element += 1

        return f"element{element}"


########################################################################################


class PartitionMathExpr(Transformer):
    def visit_MathMul(self, model: MathMul):
        priority = dict(MathImag=4, MathNum=3, MathVar=2, MathFunc=1, MathPow=0)

        if isinstance(model.expr2, (MathImag, MathNum, MathVar, MathFunc, MathPow)):
            if isinstance(model.expr1, MathMul):
                if (
                    priority[model.expr2.__class__.__name__]
                    > priority[model.expr1.expr2.__class__.__name__]
                ):
                    return MathMul(
                        expr1=self.visit(
                            MathMul(expr1=model.expr1.expr1, expr2=model.expr2)
                        ),
                        expr2=self.visit(model.expr1.expr2),
                    )
            else:
                if (
                    priority[model.expr2.__class__.__name__]
                    > priority[model.expr1.__class__.__name__]
                ):
                    return MathMul(
                        expr1=self.visit(model.expr2),
                        expr2=self.visit(model.expr1),
                    )
        return MathMul(expr1=self.visit(model.expr1), expr2=self.visit(model.expr2))


########################################################################################


class DistributeMathExpr(Transformer):
    def visit_MathMul(self, model: MathMul):
        if isinstance(model.expr1, (MathAdd, MathSub)):
            return model.expr1.__class__(
                expr1=self.visit(MathMul(expr1=model.expr1.expr1, expr2=model.expr2)),
                expr2=self.visit(MathMul(expr1=model.expr1.expr2, expr2=model.expr2)),
            )
        if isinstance(model.expr2, (MathAdd, MathSub)):
            return model.expr2.__class__(
                expr1=self.visit(MathMul(expr1=model.expr1, expr2=model.expr2.expr1)),
                expr2=self.visit(MathMul(expr1=model.expr1, expr2=model.expr2.expr2)),
            )
        return MathMul(expr1=self.visit(model.expr1), expr2=self.visit(model.expr2))

    def visit_MathSub(self, model: MathSub):
        return MathAdd(
            expr1=self.visit(model.expr1),
            expr2=MathMul(expr1=MathNum(value=-1), expr2=self.visit(model.expr2)),
        )

    def visit_MathDiv(self, model: MathDiv):
        return MathMul(
            expr1=self.visit(model.expr1),
            expr2=MathPow(expr1=self.visit(model.expr2), expr2=MathNum(value=-1)),
        )


########################################################################################


class ProperOrderMathExpr(Transformer):
    def _visit(self, model: Any):
        if isinstance(model, (MathAdd, MathMul)):
            return self.visit_MathAddMul(model)
        return super(self.__class__, self)._visit(model)

    def visit_MathAddMul(self, model: Union[MathAdd, MathMul]):
        if isinstance(model.expr2, model.__class__):
            return model.__class__(
                expr1=model.__class__(
                    expr1=self.visit(model.expr1), expr2=self.visit(model.expr2.expr1)
                ),
                expr2=self.visit(model.expr2.expr2),
            )
        return model.__class__(
            expr1=self.visit(model.expr1), expr2=self.visit(model.expr2)
        )
