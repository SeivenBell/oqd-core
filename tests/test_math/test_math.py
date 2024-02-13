from quantumion.interface.math import MathNum, MathUnary, PrintMathExpr

########################################################################################

if __name__ == "__main__":

    expr = -MathNum(value=1) + 1
    expr = 2 + -expr + 1 + -MathUnary(func="sin", arg=MathNum(value=1) + 3232) ** 2
    expr = 2**-expr
    print(expr.accept(PrintMathExpr()))
