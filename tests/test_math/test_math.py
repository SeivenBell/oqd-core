from quantumion.interface.math import MathNum, MathUnary
from quantumion.compiler.math import PrintMathExpr

########################################################################################

if __name__ == "__main__":

    expr = -MathNum(value=1) + 1
    expr = 2**-expr
    expr = 2 + -expr + 1 + -MathUnary(func="sin", arg=MathNum(value=1) + 3232) ** 2
    print(expr.accept(PrintMathExpr()))
