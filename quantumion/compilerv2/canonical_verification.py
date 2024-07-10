from quantumion.compilerv2.base import PassBase
from quantumion.compilerv2.generic import *
from quantumion.compilerv2.rule import *
from quantumion.compilerv2.walk import *
from quantumion.interface.math import *
from rich import print as pprint
from quantumion.compiler.analog.error import CanonicalFormError
from quantumion.interface.analog import *
from typing import Union
from quantumion.compiler.analog.base import *

class CanVerPauliAlgebra(RewriteRule):
    """
    Assumptions:
    Distributed, Gathered and then proper ordered. Then MatMul is done on the set of operators.
    """

    def map_OperatorMul(self, model: OperatorMul):
        pprint(model)
        if isinstance(model.op1, Pauli) and isinstance(model.op2, Pauli):
            raise CanonicalFormError("Incomplete Pauli Algebra")
        else:
            return None

    # def map_Operator(self, model):
    #     pass            
class PruneIdentity(RewriteRule):
    """
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli, NormalOrder
    """

    """
    There is pattern matching involved. when we go to visit_Op, we go to the pattern Op and then the 
    inner if statements try to do pattern matching
    if no pattern matched for the given Op model which has been visited, we just return None
    """
    def map_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, (Identity)):
            return model.op2
        pprint("model.op1 {}".format(model.op1))
        pprint("self {}".format(self.map))
        if isinstance(model.op2, (Identity)):
            return model.op1 # problem is this is a rule and not a walk !!
        return None
    
    # def map_OperatorTerminal(self, model):
    #     return model

class PauliAlgebra(RewriteRule):
    """
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder
    """

    def map_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, Pauli) and isinstance(model.op2, Pauli):
            if isinstance(model.op1, PauliI):
                return model.op2
            if isinstance(model.op2, PauliI):
                return model.op1
            if model.op1 == model.op2:
                return PauliI()
            if isinstance(model.op1, PauliX) and isinstance(model.op2, PauliY):
                return OperatorScalarMul(op=PauliZ(), expr=MathImag())
            if isinstance(model.op1, PauliY) and isinstance(model.op2, PauliZ):
                return OperatorScalarMul(op=PauliX(), expr=MathImag())
            if isinstance(model.op1, PauliZ) and isinstance(model.op2, PauliX):
                return OperatorScalarMul(op=PauliY(), expr=MathImag())
            return OperatorScalarMul(
                op=OperatorMul(op1=model.op2, op2=model.op1),
                expr=MathNum(value=-1),
            )
        return None

class OperatorDistribute(RewriteRule):
    """
    Assumptions: GatherMathExpr (sometimes)
    """
    # def map_OperatorTerminal(self, model: OperatorTerminal):
    #     return None # rule is do nothing

    def map_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, (OperatorAdd, OperatorSub)):
            return model.op1.__class__(
                op1=OperatorMul(op1=model.op1.op1, op2=model.op2),
                op2=OperatorMul(op1=model.op1.op2, op2=model.op2),
            )
        if isinstance(model.op2, (OperatorAdd, OperatorSub)):
            return model.op2.__class__(
                op1=OperatorMul(op1=model.op1, op2=model.op2.op1),
                op2=OperatorMul(op1=model.op1, op2=model.op2.op2),
            )
        if isinstance(model.op1, (OperatorKron)) and isinstance(
            model.op2, (OperatorKron)
        ):
            return OperatorKron(
                op1=OperatorMul(op1=model.op1.op1, op2=model.op2.op1),
                op2=OperatorMul(op1=model.op1.op2, op2=model.op2.op2),
            )
        return None

    def map_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op1, (OperatorAdd, OperatorSub)):
            return model.op1.__class__(
                op1=OperatorKron(op1=model.op1.op1, op2=model.op2),
                op2=OperatorKron(op1=model.op1.op2, op2=model.op2),
            )
        if isinstance(model.op2, (OperatorAdd, OperatorSub)):
            return model.op2.__class__(
                op1=OperatorKron(op1=model.op1, op2=model.op2.op1),
                op2=OperatorKron(op1=model.op1, op2=model.op2.op2),
            )
        return None

    def map_OperatorScalarMul(self, model: OperatorScalarMul):
        # # return None
        """
        If logic here is commented out, then for  2*(X@(A+C)+Y) I get

            OperatorScalarMul(
                class_='OperatorScalarMul',
                op=OperatorAdd(
                    class_='OperatorAdd',
                    op1=OperatorAdd(
                        class_='OperatorAdd',
                        op1=OperatorKron(class_='OperatorKron', op1=PauliX(class_='PauliX'), op2=Annihilation(class_='Annihilation')),
                        op2=OperatorKron(class_='OperatorKron', op1=PauliX(class_='PauliX'), op2=Creation(class_='Creation'))
                    ),
                    op2=PauliY(class_='PauliY')
                ),
                expr=MathNum(class_='MathNum', value=2)
            )
        
        if not commented out, for same thing we get:
        

            OperatorAdd(
                class_='OperatorAdd',
                op1=OperatorScalarMul(
                    class_='OperatorScalarMul',
                    op=OperatorAdd(
                        class_='OperatorAdd',
                        op1=OperatorKron(class_='OperatorKron', op1=PauliX(class_='PauliX'), op2=Annihilation(class_='Annihilation')),
                        op2=OperatorKron(class_='OperatorKron', op1=PauliX(class_='PauliX'), op2=Creation(class_='Creation'))
                    ),
                    expr=MathNum(class_='MathNum', value=2)
                ),
                op2=OperatorScalarMul(class_='OperatorScalarMul', op=PauliY(class_='PauliY'), expr=MathNum(class_='MathNum', value=2))
            )
        """
        if isinstance(model.op, (OperatorAdd, OperatorSub)):
            return model.op.__class__(
                op1=OperatorScalarMul(op=model.op.op1, expr=model.expr),
                op2=OperatorScalarMul(op=model.op.op2, expr=model.expr),
            )
        return None
        # return OperatorScalarMul(op=self.visit(model.op), expr=model.expr)

    def map_OperatorSub(self, model: OperatorSub):
        return OperatorAdd(
            op1=model.op1,
            op2=OperatorScalarMul(op=model.op2, expr=MathNum(value=-1)),
        )
    
class GatherMathExpr(RewriteRule):
    """
    Assumptions: OperatorDistribute (sometimes)
    """

    def map_OperatorScalarMul(self, model: OperatorScalarMul):
        # pprint(model)
        if isinstance(model.op, OperatorScalarMul):
            return model.expr * model.op.expr * model.op.op

        return None
    
    def map_OperatorMul(self, model: OperatorMul):
        return self._mulkron(model)
    
    def map_OperatorKron(self, model: OperatorKron):
        return self._mulkron(model)

    def _mulkron(self, model: Union[OperatorMul, OperatorKron]):
        if isinstance(model.op1, OperatorScalarMul) and isinstance(
            model.op2, OperatorScalarMul
        ):
            return (
                model.op1.expr
                * model.op2.expr
                * model.__class__(op1=model.op1.op, op2=model.op2.op)
            )
        if isinstance(model.op1, OperatorScalarMul):
            return model.op1.expr * model.__class__(op1=model.op1.op, op2=model.op2)
            
        if isinstance(model.op2, OperatorScalarMul):
            return model.op2.expr * model.__class__(op1=model.op1, op2=model.op2.op)
        return None
    
    # def visit_OperatorAdd(self, model):
    #     return None

    # def visit_OperatorAddSub(self, model: Union[OperatorAdd, OperatorSub]):
    #     return model.__class__(op1=self.visit(model.op1), op2=self.visit(model.op2))

class GatherPauli(RewriteRule):
    """
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli
    """

    def map_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op2, Pauli):
            if isinstance(model.op1, Ladder):
                return OperatorKron(
                    op1=model.op2,
                    op2=model.op1,
                )
            if isinstance(model.op1, OperatorMul) and isinstance(model.op1.op2, Ladder):
                return OperatorKron(
                    op1=model.op2,
                    op2=model.op1,
                )
            if isinstance(model.op1, OperatorKron) and isinstance(
                model.op1.op2, Union[Ladder, OperatorMul]
            ):
                return OperatorKron(
                    op1=OperatorKron(op1=model.op1.op1, op2=model.op2),
                    op2=model.op1.op2,
                )
        return None
    

class CanVerGatherMathExpr(RewriteRule):
    """Assuming that OperatorDistribute has already been fully ran"""

    def map_OperatorMul(self, model: OperatorMul):
        return self._mulkron(model)
    
    def map_OperatorKron(self, model: OperatorKron):
        return self._mulkron(model)

    def _mulkron(self, model: Union[OperatorMul, OperatorKron]):
        if isinstance(model.op1, OperatorScalarMul) or isinstance(
            model.op2, OperatorScalarMul
        ):
            raise CanonicalFormError("Incomplete Gather Math Expression")
        return None

    def map_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, OperatorScalarMul):
            raise CanonicalFormError(
                "Incomplete scalar multiplications after GatherMathExpression"
            )
        return None

class NormalOrder(RewriteRule):
    """
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli
    """

    def map_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op2, Creation):
            if isinstance(model.op1, Annihilation):
                return OperatorAdd(
                    op1=OperatorMul(op1=model.op2, op2=model.op1), op2=Identity()
                )
            if isinstance(model.op1, Identity):
                return OperatorMul(op1=model.op2, op2=model.op1)
            if isinstance(model.op1, OperatorMul) and isinstance(
                model.op1.op2, (Annihilation, Identity)
            ):
                return OperatorMul(
                    op1=model.op1.op1,
                    op2=OperatorMul(op1=model.op1.op2, op2=model.op2),
                )
        return model

class ProperOrder(RewriteRule):
    """
    Assumptions: GatherMathExpr, OperatorDistribute
    """

    def map_OperatorAdd(self, model: OperatorAdd):
        return self._addmullkron(model=model)
    
    def map_OperatorMul(self, model: OperatorMul):
        return self._addmullkron(model=model)
    
    def map_OperatorKron(self, model: OperatorKron):
        return self._addmullkron(model=model)

    def _addmullkron(
        self, model: Union[OperatorAdd, OperatorMul, OperatorKron]
    ):
        if isinstance(model.op2, model.__class__):
            return model.__class__(
                op1=model.__class__(
                    op1=model.op1, op2=model.op2.op1
                ),
                op2=model.op2.op2,
            )
        return model.__class__(op1=model.op1, op2=model.op2)
class ScaleTerms(RewriteRule):
    """
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli, NormalOrder
                 PruneIdentity
    (SortedOrder and ScaleTerms can be run in either order)
    # """
    def __init__(self):
        super().__init__()
        self.op_add_root = False

    def map_Operator(self, model: Operator):
        if not self.op_add_root:
            self.op_add_root = True
            if not isinstance(model, Union[OperatorAdd, OperatorScalarMul]):
                return OperatorScalarMul(expr=1, op=model)
        return model

    def map_OperatorAdd(self, model: OperatorAdd):
        self.op_add_root = True
        op1, op2 = model.op1, model.op2
        if not isinstance(model.op1, Union[OperatorScalarMul, OperatorAdd]):
            op1 = OperatorScalarMul(expr=1, op=model.op1)
        if not isinstance(model.op2, Union[OperatorScalarMul, OperatorAdd]):
            op2 = OperatorScalarMul(expr=1, op=model.op2)
        return OperatorAdd(op1=op1, op2=op2)

if __name__ == '__main__':
    I, X, Z, Y = PauliI(), PauliX(), PauliZ(), PauliY()
    A, C, LI = Annihilation(), Creation(), Identity()
    exp = I@Z@(X*X)*C*LI
    exp = I@I@X@(X-Z)@(A*A) + Z@(X@(X@(X+Z)))@(A*C*A*C*C)
    # exp = I@I@X@(X-Z)@(A*A) + Z@(X@(X@((X*I)+Z)))@(A*C*A*C*C)
    # exp = (C@A)*(X*Y)
    exp = Creation() * Annihilation() * Identity()  * Identity()  * Identity()  * Identity()
    exp = A*C + C*A*LI
    # exp = A*A@C*A@(LI*A)
    exp = X@(X@A)+ Y@LI
    exp = X@((2*Y)+Z)
    exp = 2*(X@(A+C)+Y)
    exp = X*(X+Y)
    # gather math expr
    exp = 2*(X@Z) + Y@Z # no change
    exp = (2*X)@Z + Y@Z # correct
    exp = X * ((2+3)*X) # correct
    exp = 2j*(X @ (A * A * C) @ (Y @ (A*C*A*A*C*LI))) + (-1)*(A*C*A*A*C*LI) # no change
    exp = 2j*(X @ (A * A * C) @ (Y @ (A*C*A*A*C*LI))) + (-1)*(A*C*A*(1*A)*C*LI) # correct
    exp = 2j*(5*(3* (X + Y)) + 3* (Z @ A*A*C*A)) # fine after 1 gather, 2 dist
    exp = (3 * 3 * 3) * ((X * Y) @ (A*C)) # no change
    exp = (3*(3*(3*(X*Y))))
    # gather pauli
    exp = X@X@Y@(A*C*LI)@A # no change
    exp = X@X@Y@(A*C*LI)@A@I # correct
    exp = X@X@Y@(A*C*LI)@A + I@I@I@I@C@C # no change
    # exp = X@X@Y@(A*C*LI)@A@I + I@I@I@I@C@C #ccorrect
    # exp = C@(A@(Z+I)) ## --> handles by repeatedly applying opdist (check with transformer)
    # exp = [A@(Z+I@(Z+Y))] # Annihilation() @ PauliZ() + Annihilation() @ (PauliI() @ PauliZ() + PauliI() @ PauliY()) done after 1 app. This is done by just 1 app. Needed for nested cases
    
    exp = A*C
    pprint(exp)
    pprint("\n------\n")
    out = Pre(ScaleTerms())(exp)
    
    # out = Pre(CanVerPauliAlgebra())(exp)
 
    pprint(out)
    pprint(out.accept(PrintOperator()))

    if out == exp:
        pprint("\n------")
        pprint(True)
        pprint("------")
    