from rich import print as pprint

########################################################################################

from quantumion.interface.math import *
from quantumion.interface.analog.operator import *

from quantumion.compiler.math import PrintMathExpr, ReorderMathExpr, DeNestMathMul
from quantumion.compiler.analog.base import PrintOperator
from quantumion.compiler.analog.canonicalize import GatherMathExpr
from quantumion.compiler.analog.verify import VerifyHilbertSpace

########################################################################################

if __name__ == "__main__":

    expr = MathStr(string="(1+2)*(2+1*(3+4*(3+5)*sin((a+2)*(6+d)**2)))")
    pprint("{:^5}:".format(0), expr.accept(PrintMathExpr()))
    for i in range(10):
        expr = expr.accept(DeNestMathMul())
        expr = expr.accept(ReorderMathExpr())
        pprint("{:^5}:".format(i + 1), expr.accept(PrintMathExpr()))

    ########################################################################################

    # expr = 1 * PauliX() @ PauliY() * MathStr(string="2") * MathStr(
    #     string="sin(w*t + -k*x)"
    # ) @ Annihilation() * (
    #     PauliI() @ (PauliZ() * 1) @ Creation() * -MathStr(string="A")
    # ) @ (
    #     PauliI() @ (PauliZ() * 1) @ Creation() * MathStr(string="A")
    # ) + (
    #     PauliI() @ (PauliZ() * 1) @ Creation() * MathStr(string="-A")
    # ) @ (
    #     PauliI() @ (PauliZ() * 1) @ -Creation() * MathStr(string="+A")
    # )

    # for i in range(10):
    #     expr = expr.accept(GatherMathExpr())
    #     pprint("\n{:^5}:".format(i + 1), expr.accept(PrintOperator()))

    # pprint(expr.accept(VerifyHilbertSpace()))
