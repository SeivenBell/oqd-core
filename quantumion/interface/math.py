from typing import Union, Literal, Annotated, Any

from pydantic import AfterValidator, BeforeValidator

import numpy as np

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel

########################################################################################


class MathExpr(TypeReflectBaseModel):

    @classmethod
    def cast(cls, value: Any):
        if isinstance(value, MathExpr):
            return value
        if isinstance(value, (int, float)):
            value = MathNum(value=value)
            return value
        if isinstance(value, (complex, np.complex128)):
            value = MathNum(value=value.real) + MathImag() * value.imag
            return value
        if isinstance(value, str):
            value = MathStr(string=value)
            return value
        raise TypeError

    def __neg__(self):
        return MathNeg(expr=self)

    def __add__(self, other):
        return MathAdd(expr1=self, expr2=other)

    def __sub__(self, other):
        return MathSub(expr1=self, expr2=other)

    def __mul__(self, other):
        return MathMul(expr1=self, expr2=other)

    def __truediv__(self, other):
        return MathDiv(expr1=self, expr2=other)

    def __pow__(self, other):
        return MathPow(expr1=self, expr2=other)

    def __radd__(self, other):
        other = MathExpr.cast(other)
        return other + self

    def __rsub__(self, other):
        other = MathExpr.cast(other)
        return other - self

    def __rmul__(self, other):
        other = MathExpr.cast(other)
        return other * self

    def __rpow__(self, other):
        other = MathExpr.cast(other)
        return other**self

    def __rtruediv__(self, other):
        other = MathExpr.cast(other)
        return other / self

    pass


########################################################################################


def is_varname(value: str) -> str:
    if not value.isidentifier():
        raise ValueError
    return value


VarName = Annotated[str, AfterValidator(is_varname)]
CastMathExpr = Annotated[MathExpr, BeforeValidator(MathExpr.cast)]
Unaries = Literal["sin", "cos", "tan", "exp", "log", "sinh", "cosh", "tanh"]


########################################################################################


class MathStr(MathExpr):
    string: str


class MathVar(MathExpr):
    name: VarName


class MathNum(MathExpr):
    value: Union[int, float]


class MathImag(MathExpr):
    pass


class MathNeg(MathExpr):
    expr: CastMathExpr


class MathUnary(MathExpr):
    func: Unaries
    expr: CastMathExpr


class MathAdd(MathExpr):
    expr1: CastMathExpr
    expr2: CastMathExpr


class MathSub(MathExpr):
    expr1: CastMathExpr
    expr2: CastMathExpr


class MathMul(MathExpr):
    expr1: CastMathExpr
    expr2: CastMathExpr


class MathDiv(MathExpr):
    expr1: CastMathExpr
    expr2: CastMathExpr


class MathPow(MathExpr):
    expr1: CastMathExpr
    expr2: CastMathExpr
