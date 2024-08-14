from typing import Union

########################################################################################

from quantumion.compiler.rule import RewriteRule
from quantumion.compiler.walk import Post
from quantumion.compiler.analog.passes.analysis import analysis_term_index
from quantumion.interface.math import MathNum, MathImag, MathAdd
from quantumion.compiler.analog.error import CanonicalFormError
from quantumion.interface.analog import *

########################################################################################

__all__ = [
    "OperatorDistribute",
    "GatherMathExpr",
    "GatherPauli",
    "PruneIdentity",
    "PauliAlgebra",
    "NormalOrder",
    "ProperOrder",
    "ScaleTerms",
    "SortedOrder",
]

########################################################################################


class OperatorDistribute(RewriteRule):
    """
    Assumptions: GatherMathExpr (sometimes)
    """

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

        if isinstance(model.op, (OperatorAdd, OperatorSub)):
            return model.op.__class__(
                op1=OperatorScalarMul(op=model.op.op1, expr=model.expr),
                op2=OperatorScalarMul(op=model.op.op2, expr=model.expr),
            )
        return None

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
        if isinstance(model.op2, (Identity)):
            return model.op1  # problem is this is a rule and not a walk !!
        return None


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

    def _addmullkron(self, model: Union[OperatorAdd, OperatorMul, OperatorKron]):
        if isinstance(model.op2, model.__class__):
            return model.__class__(
                op1=model.__class__(op1=model.op1, op2=model.op2.op1),
                op2=model.op2.op2,
            )
        return model.__class__(op1=model.op1, op2=model.op2)


class ScaleTerms(RewriteRule):
    """
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli, NormalOrder
                 PruneIdentity
    (SortedOrder and ScaleTerms can be run in either order)
    Important: Requires GatherMathExpr right after application of ScaleTerms for Post walk
    #"""

    def __init__(self):
        super().__init__()
        self.op_add_root = False

    def map_AnalogGate(self, model):
        self.op_add_root = False

    def map_Expectation(self, model):
        self.op_add_root = False

    def map_Operator(self, model: Operator):
        if not self.op_add_root:
            self.op_add_root = True
            if not isinstance(model, Union[OperatorAdd, OperatorScalarMul]):
                return OperatorScalarMul(expr=1, op=model)
        return model  # check with no ret

    def map_OperatorAdd(self, model: OperatorAdd):
        self.op_add_root = True
        op1, op2 = model.op1, model.op2
        if not isinstance(model.op1, Union[OperatorScalarMul, OperatorAdd]):
            op1 = OperatorScalarMul(expr=1, op=model.op1)
        if not isinstance(model.op2, Union[OperatorScalarMul, OperatorAdd]):
            op2 = OperatorScalarMul(expr=1, op=model.op2)
        return OperatorAdd(op1=op1, op2=op2)  # check with no ret


class SortedOrder(RewriteRule):
    """
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli, NormalOrder
                 PruneIdentity
    (SortedOrder and ScaleTerms can be run in either order)
    """

    def map_OperatorAdd(self, model: OperatorAdd):
        if isinstance(model.op1, OperatorAdd):
            term1 = analysis_term_index(model.op1.op2)
            term2 = analysis_term_index(model.op2)

            if term1 == term2:
                expr1 = (
                    model.op1.op2.expr
                    if isinstance(model.op1.op2, OperatorScalarMul)
                    else MathNum(value=1)
                )
                expr2 = (
                    model.op2.expr
                    if isinstance(model.op2, OperatorScalarMul)
                    else MathNum(value=1)
                )
                op = (
                    model.op2.op
                    if isinstance(model.op2, OperatorScalarMul)
                    else model.op2
                )
                return OperatorAdd(
                    op1=model.op1.op1,
                    op2=OperatorScalarMul(
                        op=op, expr=MathAdd(expr1=expr1, expr2=expr2)
                    ),
                )

            elif term1 > term2:
                return OperatorAdd(
                    op1=OperatorAdd(op1=model.op1.op1, op2=model.op2),
                    op2=model.op1.op2,
                )

            elif term1 < term2:
                return OperatorAdd(op1=model.op1, op2=model.op2)

        else:
            term1 = analysis_term_index(model.op1)
            term2 = analysis_term_index(model.op2)

            if term1 == term2:
                expr1 = (
                    model.op1.expr
                    if isinstance(model.op1, OperatorScalarMul)
                    else MathNum(value=1)
                )
                expr2 = (
                    model.op2.expr
                    if isinstance(model.op2, OperatorScalarMul)
                    else MathNum(value=1)
                )
                op = (
                    model.op2.op
                    if isinstance(model.op2, OperatorScalarMul)
                    else model.op2
                )
                return OperatorScalarMul(op=op, expr=MathAdd(expr1=expr1, expr2=expr2))

            elif term1 > term2:
                return OperatorAdd(
                    op1=model.op2,
                    op2=model.op1,
                )

            elif term1 < term2:
                return OperatorAdd(op1=model.op1, op2=model.op2)
