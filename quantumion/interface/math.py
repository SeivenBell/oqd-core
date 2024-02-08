from typing import Union, Literal, Annotated

from pydantic import AfterValidator

########################################################################################

from quantumion.interface.base import VisitableBaseModel, TypeReflectBaseModel

########################################################################################


class ComplexFloat(VisitableBaseModel):
    real: float
    imag: float

    @classmethod
    def from_np_complex128(cls, np_complex128):
        """Converts a numpy complex128 datatype to custom ComplexFloat"""
        return cls(real=np_complex128.real, imag=np_complex128.imag)

    def __add__(self, other):
        if isinstance(other, ComplexFloat):
            self.real += other.real
            self.imag += other.imag
            return self

        elif isinstance(other, (float, int)):
            self.real += other
            return self

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            self.real *= other
            self.imag *= other
            return self
        elif isinstance(other, ComplexFloat):
            real = self.real * other.real - self.imag * self.imag
            imag = self.real * other.imag + self.imag * self.real
            return ComplexFloat(real=real, imag=imag)
        else:
            raise TypeError

    def __radd__(self, other):
        return self + other

    def __rmul__(self, other):
        return self * other


########################################################################################


def is_varname(v: str) -> str:
    if not v.isidentifier():
        raise ValueError
    return v


def is_protectedvarname(v: str) -> str:
    if v[0] != "%" or not v[1:].isidentifier():
        raise ValueError
    return v


VarName = Annotated[str, AfterValidator(is_varname)]
ProtectedVarName = Annotated[str, AfterValidator(is_protectedvarname)]
Unaries = Literal["-", "sin", "cos", "tan", "exp", "log", "sinh", "cosh", "tanh"]

########################################################################################


class MathExpr(TypeReflectBaseModel):
    pass


class MathStr(MathExpr):
    string: str


class MathVar(MathExpr):
    name: VarName


class MathProtectedVar(MathExpr):
    name: ProtectedVarName


class MathNum(MathExpr):
    value: Union[int, float]


class MathImag(MathExpr):
    name: Literal["1j"] = "1j"


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
