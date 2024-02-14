from typing import Union, Literal, Annotated, Any

from pydantic import AfterValidator, BeforeValidator

import numpy as np

import ast

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel
from quantumion.compiler.visitor import Transform

########################################################################################

__all__ = [
    "MathExpr",
    "MathStr",
    "MathNum",
    "MathVar",
    "MathImag",
    "MathNeg",
    "MathPos",
    "MathUnary",
    "MathAdd",
    "MathSub",
    "MathMul",
    "MathDiv",
    "MathPow",
]

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
            raise TypeError(
                f'Did you forget to wrap your string ("{value}") with MathStr(string="{value}")'
            )
        raise TypeError

    def __neg__(self):
        return MathNeg(expr=self)

    def __pos__(self):
        return MathPos(expr=self)

    def __add__(self, other):
        return MathAdd(expr1=self, expr2=other)

    def __sub__(self, other):
        return MathSub(expr1=self, expr2=other)

    def __mul__(self, other):
        try:
            return MathMul(expr1=self, expr2=other)
        except:
            return other * self

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


class AST_to_MathExpr(Transform):
    def _visit(self, model: Any):
        raise TypeError

    def visit_Module(self, model: ast.Module):
        if len(model.body) == 1:
            return self.visit(model.body[0])
        raise TypeError

    def visit_Expr(self, model: ast.Expr):
        return self.visit(model.value)

    def visit_Constant(self, model: ast.Constant):
        return MathNum(value=model.value)

    def visit_Name(self, model: ast.Name):
        return MathVar(name=model.id)

    def visit_BinOp(self, model: ast.BinOp):
        if isinstance(model.op, ast.Add):
            return MathAdd(expr1=self.visit(model.left), expr2=self.visit(model.right))
        if isinstance(model.op, ast.Sub):
            return MathSub(expr1=self.visit(model.left), expr2=self.visit(model.right))
        if isinstance(model.op, ast.Mult):
            return MathMul(expr1=self.visit(model.left), expr2=self.visit(model.right))
        if isinstance(model.op, ast.Div):
            return MathDiv(expr1=self.visit(model.left), expr2=self.visit(model.right))
        if isinstance(model.op, ast.Pow):
            return MathPow(expr1=self.visit(model.left), expr2=self.visit(model.right))
        raise TypeError

    def visit_UnaryOp(self, model: ast.UnaryOp):
        if isinstance(model.op, ast.USub):
            return MathNeg(expr=self.visit(model.operand))
        if isinstance(model.op, ast.UAdd):
            return MathPos(expr=self.visit(model.operand))
        raise TypeError

    def visit_Call(self, model: ast.Call):
        if len(model.args) == 1:
            return MathUnary(func=model.func.id, expr=self.visit(model.args[0]))
        raise TypeError


def MathStr(*, string):
    return AST_to_MathExpr().visit(ast.parse(string))


########################################################################################


class MathVar(MathExpr):
    name: VarName


class MathNum(MathExpr):
    value: Union[int, float]


class MathImag(MathExpr):
    pass


class MathNeg(MathExpr):
    expr: CastMathExpr


class MathPos(MathExpr):
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
