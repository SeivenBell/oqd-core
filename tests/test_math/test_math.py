from rich import print as pprint

########################################################################################

from quantumion.interface.math import *
from quantumion.interface.analog.operator import *

from quantumion.compiler.math import PrintMathExpr
from quantumion.compiler.analog.base import PrintOperator
from quantumion.compiler.analog.canonicalize import GatherMathExpr
from quantumion.compiler.analog.verify import VerifyHilbertSpace

########################################################################################

if __name__ == "__main__":

    expr = 1 * PauliX() @ PauliY() * MathStr(string="2") * MathStr(
        string="sin(w*t)"
    ) @ Annihilation() * (
        PauliI() @ (PauliZ() * 1) @ Creation() * -MathStr(string="A")
    ) @ (
        PauliI() @ (PauliZ() * 1) @ Creation() * MathStr(string="A")
    ) + (
        PauliI() @ (PauliZ() * 1) @ Creation() * MathStr(string="-A")
    ) @ (
        PauliI() @ (PauliZ() * 1) @ -Creation() * MathStr(string="+A")
    )

    for i in range(100):
        expr = expr.accept(GatherMathExpr())

    pprint(expr)

    pprint("\n +".join(expr.accept(PrintOperator()).split("+")))

    pprint(expr.accept(VerifyHilbertSpace()))
