from typing import Any

########################################################################################

from quantumion.compiler.visitor import Transform

from quantumion.datastruct.math import (
    Unaries,
    MathStr,
    MathVar,
    MathProtectedVar,
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


def bracket_match(string):
    if string[0] == "(":
        k = 1
        n = 0
        while k > 0:
            n += 1
            k += (string[n] == "(") - (string[n] == ")")

        return string[1:n], string[n + 1 :]
    else:
        return string.split(" ", 1)


class ParseMathStr(Transform):
    def _visit(self, model: Any) -> Any:
        return model

    def visit_MathStr(self, model: str):

        for unary in Unaries.__args__:
            if model.string.startswith(unary):

                expr1, remainder = bracket_match(model.string[len(unary) :])
                remainder = remainder.strip(" ")

                if remainder == "":
                    return self.visit(MathStr(string=expr1))

                operator = remainder[0]
                expr2 = remainder[1:].strip(" ")

                operator_mapping = {
                    "+": MathAdd,
                    "-": MathSub,
                    "*": MathMul,
                    "/": MathDiv,
                    "^": MathPow,
                }

                new_model = operator_mapping[operator](
                    expr1=MathUnary(func=unary, arg=self.visit(MathStr(string=expr1))),
                    expr2=self.visit(MathStr(string=expr2)),
                )

                return new_model

        if model.string[0] == "%" and model.string[1:].isidentifier():
            return MathProtectedVar(name=model.string)

        if model.string.isidentifier():
            return MathVar(name=model.string)

        if model.string == "1j":
            return MathImag()

        try:
            return MathNum(value=float(model.string))
        except:
            pass

        expr1, remainder = bracket_match(model.string)
        remainder = remainder.strip(" ")

        if remainder == "":
            return self.visit(MathStr(string=expr1))

        operator = remainder[0]
        expr2 = remainder[1:].strip(" ")

        operator_mapping = {
            "+": MathAdd,
            "-": MathSub,
            "*": MathMul,
            "/": MathDiv,
            "^": MathPow,
        }

        new_model = operator_mapping[operator](
            expr1=self.visit(MathStr(string=expr1)),
            expr2=self.visit(MathStr(string=expr2)),
        )

        return new_model


########################################################################################


class PrintMathExpr(Transform):
    def _visit(self, model: Any):
        raise TypeError("Incompatible type for input model")

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
    s = "-1j + (a + b + c) - k / (e + 1.2e1) * (d + %e)"
    expr = MathStr(string=s)
    model = expr.accept(ParseMathStr())

    # print(model)

    print(model.accept(PrintMathExpr()))
