from typing import Union

import math

########################################################################################

from quantumion.interface.math import *
from quantumion.compilerv2.rule import *

########################################################################################

__all__ = [
    "PrintMathExpr",
    "DistributeMathExpr",
    "PartitionMathExpr",
    "ProperOrderMathExpr",
    "EvaluateMathExpr",
]

########################################################################################


class PrintMathExpr(ConversionRule):
    def __init__(self, *, verbose=False):
        super().__init__()

        self.verbose = verbose

    def map_MathVar(self, model: MathVar, operands):
        string = "{}".format(model.name)
        return string

    def map_MathNum(self, model: MathNum, operands):
        string = "{}".format(model.value)
        return string

    def map_MathImag(self, model: MathImag, operands):
        string = "1j"
        return string

    def map_MathFunc(self, model: MathFunc, operands):
        string = "{}({})".format(model.func, operands["expr"])
        return string

    def map_MathAdd(self, model: MathAdd, operands):
        if self.verbose:
            return self._map_MathBinaryOp(model, operands)
        string = "{} + {}".format(operands["expr1"], operands["expr2"])
        return string

    def map_MathSub(self, model: MathSub, operands):
        if self.verbose:
            return self._map_MathBinaryOp(model, operands)
        s2 = (
            f"({operands['expr2']})"
            if isinstance(model.expr2, (MathAdd, MathSub))
            else operands["expr2"]
        )
        string = "{} - {}".format(operands["expr1"], s2)
        return string

    ##
    def map_MathMul(self, model: MathMul, operands):
        if self.verbose:
            return self._map_MathBinaryOp(model, operands)
        s1 = (
            f"({operands['expr1']})"
            if isinstance(operands["expr1"], (MathAdd, MathSub))
            else operands["expr1"]
        )
        s2 = (
            f"({operands['expr2']})"
            if isinstance(model.expr2, (MathAdd, MathSub))
            else operands["expr2"]
        )

        string = "{} * {}".format(s1, s2)
        return string

    def map_MathDiv(self, model: MathDiv, operands):
        if self.verbose:
            return self._map_MathBinaryOp(model, operands)
        s1 = (
            f"({operands['expr1']})"
            if isinstance(model.expr1, (MathAdd, MathSub))
            else operands["expr1"]
        )
        s2 = (
            f"({operands['expr2']})"
            if isinstance(model.expr2, (MathAdd, MathSub))
            else operands["expr2"]
        )

        string = "{} / {}".format(s1, s2)
        return string

    def map_MathPow(self, model: MathPow, operands):
        if self.verbose:
            return self._map_MathBinaryOp(model, operands)
        s1 = (
            f"({operands['expr1']})"
            if isinstance(model.expr1, (MathAdd, MathSub, MathMul, MathDiv))
            else operands["expr1"]
        )
        s2 = (
            f"({operands['expr2']})"
            if isinstance(model.expr2, (MathAdd, MathSub, MathMul, MathDiv))
            else operands["expr2"]
        )

        string = "{} ** {}".format(s1, s2)
        return string

    def _map_MathBinaryOp(self, model: MathBinaryOp, operands):
        s1 = (
            f"({operands['expr1']})"
            if not isinstance(model.expr1, (MathTerminal, MathUnaryOp))
            else operands["expr1"]
        )
        s2 = (
            f"({operands['expr2']})"
            if not isinstance(model.expr2, (MathTerminal, MathUnaryOp))
            else operands["expr2"]
        )
        operator_dict = dict(
            MathAdd="+", MathSub="-", MathMul="*", MathDiv="/", MathPow="**"
        )
        string = f"{s1} {operator_dict[model.__class__.__name__]} {s2}"
        return string


########################################################################################


class DistributeMathExpr(RewriteRule):
    def map_MathMul(self, model: MathMul):
        if isinstance(model.expr1, (MathAdd, MathSub)):
            return model.expr1.__class__(
                expr1=MathMul(expr1=model.expr1.expr1, expr2=model.expr2),
                expr2=MathMul(expr1=model.expr1.expr2, expr2=model.expr2),
            )
        if isinstance(model.expr2, (MathAdd, MathSub)):
            return model.expr2.__class__(
                expr1=MathMul(expr1=model.expr1, expr2=model.expr2.expr1),
                expr2=MathMul(expr1=model.expr1, expr2=model.expr2.expr2),
            )
        pass

    def map_MathSub(self, model: MathSub):
        return MathAdd(
            expr1=model.expr1,
            expr2=MathMul(expr1=MathNum(value=-1), expr2=model.expr2),
        )

    def map_MathDiv(self, model: MathDiv):
        return MathMul(
            expr1=model.expr1,
            expr2=MathPow(expr1=model.expr2, expr2=MathNum(value=-1)),
        )


class PartitionMathExpr(RewriteRule):
    def map_MathMul(self, model: MathMul):
        priority = dict(MathImag=4, MathNum=3, MathVar=2, MathFunc=1, MathPow=0)

        if isinstance(model.expr2, (MathImag, MathNum, MathVar, MathFunc, MathPow)):
            if isinstance(model.expr1, MathMul):
                if (
                    priority[model.expr2.__class__.__name__]
                    > priority[model.expr1.expr2.__class__.__name__]
                ):
                    return MathMul(
                        expr1=MathMul(expr1=model.expr1.expr1, expr2=model.expr2),
                        expr2=model.expr1.expr2,
                    )
            else:
                if (
                    priority[model.expr2.__class__.__name__]
                    > priority[model.expr1.__class__.__name__]
                ):
                    return MathMul(
                        expr1=model.expr2,
                        expr2=model.expr1,
                    )
        pass


class ProperOrderMathExpr(RewriteRule):

    def map_MathAdd(self, model: MathAdd):
        return self._MathAddMul(model)

    def map_MathMul(self, model: MathMul):
        return self._MathAddMul(model)

    def _MathAddMul(self, model: Union[MathAdd, MathMul]):
        if isinstance(model.expr2, model.__class__):
            return model.__class__(
                expr1=model.__class__(expr1=model.expr1, expr2=model.expr2.expr1),
                expr2=model.expr2.expr2,
            )
        pass


########################################################################################


class EvaluateMathExpr(ConversionRule):
    def map_MathVar(self, model: MathVar, operands):
        raise TypeError

    def map_MathNum(self, model: MathNum, operands):
        return model.value

    def map_MathImag(self, model: MathImag, operands):
        return complex("1j")  # 1j also works

    def map_MathFunc(self, model: MathFunc, operands):
        return getattr(math, model.func)(operands["expr"])

    def map_MathAdd(self, model: MathAdd, operands):
        return operands["expr1"] + operands["expr2"]

    def map_MathSub(self, model: MathSub, operands):
        return operands["expr1"] - operands["expr2"]

    def map_MathMul(self, model: MathMul, operands):
        return operands["expr1"] * operands["expr2"]

    def map_MathDiv(self, model: MathDiv, operands):
        return operands["expr1"] / operands["expr2"]

    def map_MathPow(self, model: MathPow, operands):
        return operands["expr1"] ** operands["expr2"]
