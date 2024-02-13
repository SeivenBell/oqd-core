from typing import Any

########################################################################################

from quantumion.compiler.visitor import Transform

from quantumion.interface.math import (
    MathStr,
    MathVar,
    MathNeg,
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

    def visit_MathStr(self, model: MathStr):
        return f"({model.string})"

    def visit_MathVar(self, model: MathVar):
        string = "{}".format(model.name)
        return string

    def visit_MathNum(self, model: MathNum):
        string = "{}".format(model.value)
        return string

    def visit_MathImag(self, model: MathImag):
        string = "1j"
        return string

    def visit_MathNeg(self, model: MathNeg):
        if not isinstance(
            model.expr, (MathAdd, MathSub, MathDiv, MathMul, MathDiv, MathPow)
        ):
            string = "-{}".format(self.visit(model.expr))
        else:
            string = "-({})".format(self.visit(model.expr))
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


########################################################################################

if __name__ == "__main__":
    import ast

    class ASTVisitor(Transform):
        def _visit(self, model: Any):
            raise TypeError

        def visit_Module(self, model: ast.Module):
            return self.visit(model.body[0])

        def visit_Expr(self, model: ast.Expr):
            return self.visit(model.value)

        def visit_Constant(self, model: ast.Constant):
            return MathNum(value=model.value)

        def visit_Name(self, model: ast.Name):
            return MathVar(name=model.id)

        def visit_BinOp(self, model: ast.BinOp):
            if isinstance(model.op, ast.Add):
                return MathAdd(
                    expr1=self.visit(model.left), expr2=self.visit(model.right)
                )
            if isinstance(model.op, ast.Sub):
                return MathSub(
                    expr1=self.visit(model.left), expr2=self.visit(model.right)
                )
            if isinstance(model.op, ast.Mult):
                return MathMul(
                    expr1=self.visit(model.left), expr2=self.visit(model.right)
                )
            if isinstance(model.op, ast.Div):
                return MathDiv(
                    expr1=self.visit(model.left), expr2=self.visit(model.right)
                )

        def visit_UnaryOp(self, model: ast.UnaryOp):
            return MathNeg(expr=self.visit(model.operand))

        def visit_Call(self, model: ast.Call):
            print(model.func.id, model.args[0])
            return MathUnary(func=model.func.id, expr=self.visit(model.args[0]))
