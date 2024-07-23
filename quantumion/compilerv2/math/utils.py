from typing import Any, Union

########################################################################################

from quantumion.interface.math import *
from quantumion.compilerv2.rule import *
from quantumion.compilerv2.walk import *
import math

########################################################################################
from rich import print as pprint



class PrintMathExpr(ConversionRule):

    def map_MathVar(self, model: MathVar, operands):
        string = "{}".format(model.name)
        return string

    def map_MathNum(self, model: MathNum, operands):
        string = "{}".format(model.value)
        return string

    def map_MathImag(self, model: MathImag, operands):
        string = "1j"
        return string

    def map_MathFunc(self, model: MathFunc, operands):
        string = "{}({})".format(model.func, operands['expr'])
        return string

    def map_MathAdd(self, model: MathAdd, operands):
        string = "{} + {}".format(operands['expr1'], operands['expr2'])
        return string

    def map_MathSub(self, model: MathSub, operands):
        s2 = (
            f"({operands['expr2']})"
            if isinstance(model.expr2, (MathAdd, MathSub))
            else operands['expr2']
        )
        string = "{} - {}".format(operands['expr1'], s2)
        return string
    ##
    def map_MathMul(self, model: MathMul, operands):
        s1 = (
            f"({operands['expr1']})"
            if isinstance(operands['expr1'], (MathAdd, MathSub))
            else operands['expr1']
        )
        s2 = (
            f"({operands['expr2']})"
            if isinstance(model.expr2, (MathAdd, MathSub))
            else operands['expr2']
        )

        string = "{} * {}".format(s1, s2)
        return string

    def map_MathDiv(self, model: MathDiv, operands):
        s1 = (
            f"({operands['expr1']})"
            if isinstance(model.expr1, (MathAdd, MathSub))
            else operands['expr1']
        )
        s2 = (
            f"({operands['expr2']})"
            if isinstance(model.expr2, (MathAdd, MathSub))
            else operands['expr2']
        )

        string = "{} / {}".format(s1, s2)
        return string

    def map_MathPow(self, model: MathPow, operands):
        s1 = (
            f"({operands['expr1']})"
            if isinstance(model.expr1, (MathAdd, MathSub, MathMul, MathDiv))
            else operands['expr1']
        )
        s2 = (
            f"({operands['expr2']})"
            if isinstance(model.expr2, (MathAdd, MathSub, MathMul, MathDiv))
            else operands['expr2']
        )

        string = "{} ** {}".format(s1, s2)
        return string
    
if __name__ == '__main__':
    exp = MathStr(string='3+(5*3)')
    pprint(PostConversion(PrintMathExpr())(exp))