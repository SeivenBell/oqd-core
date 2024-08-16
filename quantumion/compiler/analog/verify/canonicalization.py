from typing import Union

########################################################################################

from quantumion.compiler.rule import RewriteRule
from quantumion.interface.math import *
from quantumion.compiler.analog.error import CanonicalFormError
from quantumion.interface.analog import *
from quantumion.compiler.analog.passes.analysis import analysis_term_index
########################################################################################

__all__ = [
    "CanVerPauliAlgebra",
    "CanVerGatherMathExpr",
    "CanVerOperatorDistribute",
    "CanVerProperOrder",
    "CanVerPruneIdentity",
    "CanVerGatherPauli",
    "CanVerNormalOrder",
    "CanVerSortedOrder",
    "CanVerScaleTerm",
]

########################################################################################


class CanVerPauliAlgebra(RewriteRule):
    """
    This checks whether there is no incomplete Pauli Algebra computation
    Assumptions:
    Distributed, Gathered and then proper ordered
    """

    def map_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, Pauli) and isinstance(model.op2, Pauli):
            raise CanonicalFormError("Incomplete Pauli Algebra")
        elif isinstance(model.op1, Pauli) and isinstance(model.op2, Ladder):
            raise CanonicalFormError("Incorrect Ladder and Pauli multiplication")
        elif isinstance(model.op1, Ladder) and isinstance(model.op2, Pauli):
            raise CanonicalFormError("Incorrect Ladder and Pauli multiplication")
        pass


class CanVerGatherMathExpr(RewriteRule):
    """
    This checks whether all MathExpr have been gathered
    Assumptions: OperatorDistribute
    """

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


class CanVerOperatorDistribute(RewriteRule):
    """
    This checks for incomplete distribution of Operators
    Assumptions: None
    """
    def __init__(self):
        super().__init__()
        self.allowed_ops = Union[
            OperatorTerminal,
            Ladder,
            OperatorMul,
            OperatorScalarMul,
            OperatorKron,
        ]

    def map_OperatorMul(self, model):
        return self._OperatorMulKron(model)

    def map_OperatorKron(self, model):
        return self._OperatorMulKron(model)

    def _OperatorMulKron(self, model: Union[OperatorMul, OperatorKron]):
        if (
            isinstance(model, OperatorMul)
            and isinstance(model.op1, OperatorKron)
            and isinstance(model.op2, OperatorKron)
        ):
            raise CanonicalFormError(
                "Incomplete Operator Distribution (multiplication of OperatorKron present)"
            )
        elif not (
            isinstance(model.op1, self.allowed_ops)
            and isinstance(model.op2, self.allowed_ops)
        ):
            raise CanonicalFormError("Incomplete Operator Distribution")

        pass

    def map_OperatorScalarMul(self, model: OperatorScalarMul):
        if not (isinstance(model.op, self.allowed_ops)):
            raise CanonicalFormError(
                "Scalar multiplication of operators not simplified fully"
            )
        pass

    def map_OperatorSub(self, model: OperatorSub):
        if isinstance(model, OperatorSub):
            raise CanonicalFormError("Subtraction of terms present")
        pass


class CanVerProperOrder(RewriteRule):
    """
    This ensures that Operarors follow ProperOrder
    Example: X @ (Y @ Z) is not ProperOrder, but (X @ Y) @ Z is
    Assumptions: None
    """

    def map_OperatorAdd(self, model: OperatorAdd):
        self._OperatorAddMulKron(model)
        pass

    def map_OperatorMul(self, model: OperatorMul):
        self._OperatorAddMulKron(model)
        pass

    def map_OperatorKron(self, model: OperatorKron):
        self._OperatorAddMulKron(model)
        pass

    def _OperatorAddMulKron(self, model: Union[OperatorAdd, OperatorMul, OperatorKron]):
        if isinstance(model.op2, model.__class__):
            raise CanonicalFormError("Incorrect Proper Ordering")
        pass

    def map_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, model.__class__):
            raise CanonicalFormError(
                "Incorrect Proper Ordering (for scalar multiplication)"
            )
        pass


class CanVerPruneIdentity(RewriteRule):
    """
    This checks if there is any ladder Identity present in ladder multiplication
    Assumptions: OperatorDistribute
    """

    def map_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, Identity) or isinstance(model.op2, Identity):
            raise CanonicalFormError("Prune Identity is not complete")
        pass


class CanVerGatherPauli(RewriteRule):
    """
    This checks whether pauli and ladder have been separated. Example:
    - X @ A @ Y will fail this check
    - X @ Y @ A will pass this check
    Assumptions: Distributed, Gathered and then proper ordered and PauliAlgebra
    """

    def map_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op2, Pauli):
            if isinstance(model.op1, (Ladder, OperatorMul)):
                raise CanonicalFormError("Incorrect GatherPauli")
            if isinstance(model.op1, OperatorKron):
                if isinstance(model.op1.op2, (Ladder, OperatorMul)):
                    raise CanonicalFormError("Incorrect GatherPauli")
        pass


class CanVerNormalOrder(RewriteRule):
    """
    This checks whether the ladder operations are in normal order
    Assumptions: Distributed, Gathered and then proper ordered and PauliAlgebra, PruneIdentity
    """

    def map_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op2, Creation):
            if isinstance(model.op1, Annihilation):
                raise CanonicalFormError("Incorrect NormalOrder")
            if isinstance(model.op1, OperatorMul):
                if isinstance(model.op1.op2, Annihilation):
                    raise CanonicalFormError("Incorrect NormalOrder")
        pass

class CanVerSortedOrder(RewriteRule):
    """
    This checks whether operators are in sorted order. Example:
    - X + I will fail this check
    - I + X will pass
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli, NormalOrder
                 PruneIdentity
    """

    def map_OperatorAdd(self, model: OperatorAdd):
        term2 = analysis_term_index(model.op2)
        if isinstance(model.op1, OperatorAdd):
            term1 = analysis_term_index(model.op1.op2)
        else:
            term1 = analysis_term_index(model.op1)
        if term1 > term2:
            raise CanonicalFormError("Terms are not in sorted order")
        elif term1 == term2:
            raise CanonicalFormError("Duplicate terms present")
        pass


class CanVerScaleTerm(RewriteRule):
    """
    This cheks whether all terms have a scalar multiplication. Example:
    - X + 2*Y will fail this check
    - 1*X + 2*Y will pass this
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli, NormalOrder, PruneIdentity
    Note that this only works for Pre
    """

    def __init__(self):
        super().__init__()
        self._single_term_scaling_needed = False

    def map_AnalogGate(self, model):
        self._single_term_scaling_needed = False

    def map_Expectation(self, model):
        self._single_term_scaling_needed = False

    def map_OperatorScalarMul(self, model: OperatorScalarMul):
        self._single_term_scaling_needed = True
        pass

    def map_OperatorMul(self, model: OperatorMul):
        if not self._single_term_scaling_needed:
            raise CanonicalFormError("Single term operator has not been scaled")

    def map_OperatorKron(self, model: OperatorKron):
        if not self._single_term_scaling_needed:
            raise CanonicalFormError("Single term operator has not been scaled")

    def map_OperatorTerminal(self, model: OperatorKron):
        if not self._single_term_scaling_needed:
            raise CanonicalFormError("Single term operator has not been scaled")

    def map_OperatorAdd(self, model: OperatorAdd):
        self._single_term_scaling_needed = True
        if isinstance(model.op2, OperatorScalarMul) and isinstance(
            model.op1, Union[OperatorScalarMul, OperatorAdd]
        ):
            pass
        else:
            raise CanonicalFormError(
                "some operators between addition are not scaled properly"
            )
