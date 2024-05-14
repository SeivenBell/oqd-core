from typing import Union, Literal, Annotated, Any

from pydantic import AfterValidator, BeforeValidator

import numpy as np

import ast

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel
from quantumion.compiler.visitor import Transformer

########################################################################################

__all__ = [
    "MathExpr",
    "MathTerminal",
    "MathStr",
    "MathNum",
    "MathVar",
    "MathImag",
    "MathUnaryOp",
    "MathFunc",
    "MathBinaryOp",
    "MathAdd",
    "MathSub",
    "MathMul",
    "MathDiv",
    "MathPow",
]

########################################################################################


class MathExpr(TypeReflectBaseModel):
    """
    Class representing the abstract syntax tree (AST) for a mathematical expression
    """

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
                "Tried to cast a string to MathExpr. "
                + f'Wrap your string ("{value}") with MathStr(string="{value}").'
            )
        raise TypeError

    def __neg__(self):
        return MathMul(expr1=MathNum(value=-1), expr2=self)

    def __pos__(self):
        return self

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
Functions = Literal["sin", "cos", "tan", "exp", "log", "sinh", "cosh", "tanh"]


########################################################################################


class AST_to_MathExpr(Transformer):
    def _visit(self, model: Any):
        raise TypeError

    def visit_Module(self, model: ast.Module):
        if len(model.body) == 1:
            return self.visit(model.body[0])
        raise TypeError

    def visit_Expr(self, model: ast.Expr):
        return self.visit(model.value)

    def visit_Constant(self, model: ast.Constant):
        return MathExpr.cast(model.value)

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
            return -self.visit(model.operand)
        if isinstance(model.op, ast.UAdd):
            return self.visit(model.operand)
        raise TypeError

    def visit_Call(self, model: ast.Call):
        if len(model.args) == 1:
            return MathFunc(func=model.func.id, expr=self.visit(model.args[0]))
        raise TypeError


def MathStr(*, string):
    return AST_to_MathExpr().visit(ast.parse(string))


########################################################################################


class MathTerminal(MathExpr):
    """
    Class representing a terminal in the [`MathExpr`][quantumion.interface.math.MathExpr] abstract syntax tree (AST)
    """

    pass


class MathVar(MathTerminal):
    """
    Class representing a variable in a [`MathExpr`][quantumion.interface.math.MathExpr]
    """

    name: VarName


class MathNum(MathTerminal):
    """
    Class representing a number in a [`MathExpr`][quantumion.interface.math.MathExpr]
    """

    value: Union[int, float]


class MathImag(MathTerminal):
    """
    Class representing the imaginary unit in a [`MathExpr`][quantumion.interface.math.MathExpr] abstract syntax tree (AST)
    """

    pass


class MathUnaryOp(MathExpr):
    """
    Class representing a unary operations on a [`MathExpr`][quantumion.interface.math.MathExpr] abstract syntax tree (AST)
    """

    pass


class MathFunc(MathUnaryOp):
    """
    Class representing a named function applied to a [`MathExpr`][quantumion.interface.math.MathExpr] abstract syntax tree (AST)

    Attributes:
        func (Literal["sin", "cos", "tan", "exp", "log", "sinh", "cosh", "tanh"]): Named function to apply
        expr (MathExpr): Argument of the named function
    """

    func: Functions
    expr: CastMathExpr


class MathBinaryOp(MathExpr):
    """
    Class representing binary operations on [`MathExprs`][quantumion.interface.math.MathExpr] abstract syntax tree (AST)
    """

    pass


class MathAdd(MathBinaryOp):
    """
    Class representing the addition of [`MathExprs`][quantumion.interface.analog.operator.Operator]

    Attributes:
        expr1 (MathExpr): Left hand side [`MathExpr`][quantumion.interface.analog.operator.Operator]
        expr2 (MathExpr): Right hand side [`MathExpr`][quantumion.interface.analog.operator.Operator]
    """

    expr1: CastMathExpr
    expr2: CastMathExpr


class MathSub(MathBinaryOp):
    """
    Class representing the subtraction of [`MathExprs`][quantumion.interface.math.MathExpr]

    Attributes:
        expr1 (MathExpr): Left hand side [`MathExpr`][quantumion.interface.math.MathExpr]
        expr2 (MathExpr): Right hand side [`MathExpr`][quantumion.interface.math.MathExpr]
    """

    expr1: CastMathExpr
    expr2: CastMathExpr


class MathMul(MathBinaryOp):
    """
    Class representing the multiplication of [`MathExprs`][quantumion.interface.math.MathExpr]

    Attributes:
        expr1 (MathExpr): Left hand side [`MathExpr`][quantumion.interface.math.MathExpr]
        expr2 (MathExpr): Right hand side [`MathExpr`][quantumion.interface.math.MathExpr]
    """

    expr1: CastMathExpr
    expr2: CastMathExpr


class MathDiv(MathBinaryOp):
    """
    Class representing the division of [`MathExprs`][quantumion.interface.math.MathExpr]

    Attributes:
        expr1 (MathExpr): Left hand side [`MathExpr`][quantumion.interface.math.MathExpr]
        expr2 (MathExpr): Right hand side [`MathExpr`][quantumion.interface.math.MathExpr]
    """

    expr1: CastMathExpr
    expr2: CastMathExpr


class MathPow(MathBinaryOp):
    """
    Class representing the exponentiation of [`MathExprs`][quantumion.interface.math.MathExpr]

    Attributes:
        expr1 (MathExpr): Left hand side [`MathExpr`][quantumion.interface.math.MathExpr]
        expr2 (MathExpr): Right hand side [`MathExpr`][quantumion.interface.math.MathExpr]
    """

    expr1: CastMathExpr
    expr2: CastMathExpr
