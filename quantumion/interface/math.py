from typing import Union, Literal, Annotated, Any

from pydantic import AfterValidator

import numpy as np

########################################################################################

from quantumion.interface.base import VisitableBaseModel, TypeReflectBaseModel
from quantumion.compiler.visitor import Transform


########################################################################################


def is_varname(v: str) -> str:
    if not v.isidentifier():
        raise ValueError
    return v


VarName = Annotated[str, AfterValidator(is_varname)]
Unaries = Literal["sin", "cos", "tan", "exp", "log", "sinh", "cosh", "tanh"]

########################################################################################


class MathExpr(TypeReflectBaseModel):

    def __neg__(self):
        return MathNeg(expr=self)

    def __add__(self, other):
        other = MathExpr.convert(other)

        return MathAdd(expr1=self, expr2=other)

    def __sub__(self, other):
        other = MathExpr.convert(other)

        return MathSub(expr1=self, expr2=other)

    def __mul__(self, other):
        try:
            other = MathExpr.convert(other)
            return MathMul(expr1=self, expr2=other)
        except:
            return other * self

    def __truediv__(self, other):
        other = MathExpr.convert(other)
        return MathDiv(expr1=self, expr2=other)

    def __pow__(self, other):
        other = MathExpr.convert(other)

        return MathPow(expr1=self, expr2=other)

    def __radd__(self, other):
        other = MathExpr.convert(other)
        return other + self

    def __rsub__(self, other):
        other = MathExpr.convert(other)
        return other - self

    def __rmul__(self, other):
        other = MathExpr.convert(other)
        return other * self

    def __rpow__(self, other):
        other = MathExpr.convert(other)
        return other**self

    def __rtruediv__(self, other):
        other = MathExpr.convert(other)
        return other / self

    @classmethod
    def convert(cls, value):
        if isinstance(value, MathExpr):
            return value
        if isinstance(value, (int, float)):
            value = MathNum(value=value)
            return value
        if isinstance(value, np.complex128):
            value = MathExpr._convert_complex128(value)
            return value
        if isinstance(value, str):
            value = MathStr(string=value)
            return value
        raise TypeError

    @classmethod
    def _convert_complex128(cls, value):
        """Converts a numpy complex128 datatype to custom ComplexFloat"""
        assert isinstance(value, np.complex128)
        return MathNum(value=value.real) + MathImag() * value.imag

    pass


########################################################################################


class MathStr(MathExpr):
    string: str


class MathVar(MathExpr):
    name: VarName


class MathNum(MathExpr):
    value: Union[int, float]


class MathImag(MathExpr):
    name: Literal["1j"] = "1j"


class MathNeg(MathExpr):
    expr: MathExpr


class MathUnary(MathExpr):
    func: Unaries
    arg: MathExpr


class MathAdd(MathExpr):
    expr1: MathExpr
    expr2: MathExpr


class MathSub(MathExpr):
    expr1: MathExpr
    expr2: MathExpr


class MathMul(MathExpr):
    expr1: MathExpr
    expr2: MathExpr


class MathDiv(MathExpr):
    expr1: MathExpr
    expr2: MathExpr


class MathPow(MathExpr):
    expr1: MathExpr
    expr2: MathExpr
