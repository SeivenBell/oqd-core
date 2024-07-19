from typing import Any, Union

########################################################################################

from quantumion.interface.math import *
from quantumion.compilerv2.rule import *
from quantumion.compilerv2.walk import *
import math

########################################################################################
from rich import print as pprint


########################################################################################
class DistributeMathExpr(RewriteRule):
    def map_MathMul(self, model: MathMul):
        if isinstance(model.expr1, (MathAdd, MathSub)):
            return model.expr1.__class__(
                expr1=MathMul(expr1=model.expr1.expr1, expr2=model.expr2),
                expr2=MathMul(expr1=model.expr1.expr2, expr2=model.expr2),
            )
        if isinstance(model.expr2, (MathAdd, MathSub)):
            return model.expr2.__class__(
                expr1=MathMul(expr1=model.expr1, expr2=model.expr2.expr1),
                expr2=MathMul(expr1=model.expr1, expr2=model.expr2.expr2),
            )
        pass

    def map_MathSub(self, model: MathSub):
        return MathAdd(
            expr1=model.expr1,
            expr2=MathMul(expr1=MathNum(value=-1), expr2=model.expr2),
        )

    def map_MathDiv(self, model: MathDiv):
        return MathMul(
            expr1=model.expr1,
            expr2=MathPow(expr1=model.expr2, expr2=MathNum(value=-1)),
        )

class PartitionMathExpr(RewriteRule):
    def map_MathMul(self, model: MathMul):
        priority = dict(MathImag=4, MathNum=3, MathVar=2, MathFunc=1, MathPow=0)

        if isinstance(model.expr2, (MathImag, MathNum, MathVar, MathFunc, MathPow)):
            if isinstance(model.expr1, MathMul):
                if (
                    priority[model.expr2.__class__.__name__]
                    > priority[model.expr1.expr2.__class__.__name__]
                ):
                    return MathMul(
                        expr1= MathMul(expr1=model.expr1.expr1, expr2=model.expr2),
                        expr2=model.expr1.expr2,
                    )
            else:
                if (
                    priority[model.expr2.__class__.__name__]
                    > priority[model.expr1.__class__.__name__]
                ):
                    return MathMul(
                        expr1=model.expr2,
                        expr2=model.expr1,
                    )
        pass

class ProperOrderMathExpr(RewriteRule):

    def map_MathAdd(self, model: MathAdd):
        return self._MathAddMul(model)
    
    def map_MathMul(self, model: MathMul):
        return self._MathAddMul(model)

    def _MathAddMul(self, model: Union[MathAdd, MathMul]):
        if isinstance(model.expr2, model.__class__):
            return model.__class__(
                expr1=model.__class__(
                    expr1=model.expr1, expr2=model.expr2.expr1
                ),
                expr2=model.expr2.expr2,
            )
        pass



if __name__ == '__main__':
    exp = MathStr(string='3+(5+3)')
    pprint(exp)
    # pprint(Post(DistributeMathExpr())(Post(DistributeMathExpr())(exp)))
    pprint(Pre(ProperOrderMathExpr())(exp))