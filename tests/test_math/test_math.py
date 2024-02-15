from rich import print as pprint

########################################################################################

from quantumion.interface.math import *
from quantumion.interface.analog.operator import *

from quantumion.compiler.math import *
from quantumion.compiler.analog.base import *
from quantumion.compiler.analog.canonicalize import *
from quantumion.compiler.analog.verify import *

########################################################################################

if __name__ == "__main__":

    # expr = MathStr(string="(1+2+4-5)*(2+1*(3+4*(3+5)*sin((a+2)*(6+d)**2)))")
    # pprint("{:^5}:".format(0), expr.accept(PrintMathExpr()))
    # for i in range(10):
    #     expr = expr.accept(DeNestMathMul())
    #     expr = expr.accept(ReorderMathExpr())
    #     pprint("{:^5}:".format(i + 1), expr.accept(PrintMathExpr()))

    ########################################################################################

    # expr = 1 * PauliX() @ PauliY() * MathStr(string="2") * MathStr(
    #     string="sin(w*t + -k*x)"
    # ) @ Annihilation() * (
    #     PauliI() @ (PauliZ() * 1) @ Creation() * -MathStr(string="A")
    # ) @ (
    #     PauliI() @ (PauliZ() * 1) @ Creation() * MathStr(string="A")
    # ) - (
    #     PauliI() @ (PauliZ() * 1) @ Creation() * MathStr(string="-A")
    # ) @ (
    #     PauliI() @ (PauliZ() * 1) @ -Creation() * MathStr(string="+A")
    # )

    # pprint(
    #     "\nHilbert Space  :\n\tPauli  : {}\n\tLadder : {}".format(
    #         *expr.accept(VerifyHilbertSpace())
    #     )
    # )

    # i = 0
    # while True:
    #     _expr = expr.accept(DistributeOp())
    #     if _expr == expr:
    #         break
    #     i += 1
    #     expr = _expr
    #     pprint("\n{:^5}:".format(i), "\n" + expr.accept(VerbosePrintOperator()))

    # i = 0
    # while True:
    #     _expr = expr.accept(GatherMathExpr())
    #     if _expr == expr:
    #         break
    #     i += 1
    #     expr = _expr
    #     pprint("\n{:^5}:".format(i), "\n" + expr.accept(VerbosePrintOperator()))

    # i = 0
    # while True:
    #     _expr = expr.accept(ProperKronOrder())
    #     if _expr == expr:
    #         break
    #     i += 1
    #     expr = _expr
    #     pprint("\n{:^5}:".format(i), "\n" + expr.accept(VerbosePrintOperator()))

    # i = 0
    # while True:
    #     _expr = expr.accept(SeparatePauliLadder())
    #     if _expr == expr:
    #         break
    #     i += 1
    #     expr = _expr
    #     pprint("\n{:^5}:".format(i), "\n" + expr.accept(VerbosePrintOperator()))

    ########################################################################################

    I, X, Y, Z = PauliI(), PauliX(), PauliY(), PauliZ()
    A, C, J = Annihilation(), Creation(), Identity()

    expr = A * C * C * A * C * A * C

    import re

    i = 0
    pprint("\n{:^5}:".format(i), "\n" + expr.accept(VerbosePrintOperator()))
    while True:
        _expr = expr.accept(NormalOrder())
        _expr = _expr.accept(DistributeOp())
        _expr = _expr.accept(DistributeOp())
        _expr = _expr.accept(DistributeOp())
        _expr = _expr.accept(ProperMulOrder())

        if _expr == expr:
            break
        i += 1
        expr = _expr
        pprint(
            "\n{:^5}:".format(i),
            # "\n"
            # + re.sub(
            #     "\* Identity\(\)",
            #     "",
            "\n".join(expr.accept(PrintOperator()).split("+")),
            # ),
        )
