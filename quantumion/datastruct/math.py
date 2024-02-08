from typing import Union, Literal, Annotated

from pydantic import AfterValidator

########################################################################################

from quantumion.datastruct.base import VisitableBaseModel
from quantumion.compiler.visitor import Transform

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


class MathExpr(VisitableBaseModel):

    @classmethod
    def from_string(cls, string: str):
        raise NotImplementedError

    pass


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


########################################################################################


class PrintMathExpr(Transform):
    def _visit(self):
        raise TypeError()

    def visit_MathVar(self, model: MathVar):
        string = "{}".format(model.name)
        return string

    def visit_MathProtectedVar(self, model: MathProtectedVar):
        string = "{}".format(model.name)
        return string

    def visit_MathNum(self, model: MathNum):
        string = "{}".format(model.value)
        return string

    def visit_MathImag(self, model: MathImag):
        string = "{}".format(model.name)
        return string

    def visit_MathUnary(self, model: MathUnary):
        if model.func == "-" and not isinstance(
            model.arg, (MathAdd, MathDiv, MathMul, MathDiv, MathPow)
        ):
            string = "{}{}".format(model.func, self.visit(model.arg))
        else:
            string = "{}({})".format(model.func, self.visit(model.arg))
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

        string = "{} ^ {}".format(s1, s2)
        return string


########################################################################################

if __name__ == "__main__":
    expr1 = MathSub(expr1=MathProtectedVar(name="%t"), expr2=MathVar(name="b"))
    expr2 = MathSub(
        expr1=MathMul(expr1=MathVar(name="a"), expr2=MathVar(name="b")),
        expr2=MathVar(name="c"),
    )
    expr2 = MathUnary(
        func="-",
        arg=MathUnary(
            func="sin", arg=MathPow(expr1=MathNum(value=1), expr2=MathImag())
        ),
    )
    expr3 = MathPow(
        expr1=MathMul(
            expr1=MathVar(name="a"),
            expr2=MathSub(expr1=MathVar(name="b"), expr2=MathVar(name="c")),
        ),
        expr2=MathUnary(
            func="sin", arg=MathPow(expr1=MathNum(value=1), expr2=MathImag())
        ),
    )

    pme = PrintMathExpr()
    print(expr1.accept(pme))
    print(expr2.accept(pme))
    print(expr3.accept(pme))
