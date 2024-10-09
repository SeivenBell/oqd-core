from typing import Union

from oqd_compiler_infrastructure import RewriteRule

########################################################################################

from ....interface.math import *
from ....interface.analog import *
from ..error import CanonicalFormError
from ..passes.analysis import analysis_term_index

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
    Checks whether there is any incomplete Pauli Algebra computation

    Args:
        model (VisitableBaseModel): The rule only verifies [`Operator`][midstack.interface.analog.operator.Operator] in Analog level

    Returns:
        model (VisitableBaseMode): unchanged

    Assumptions:
        [`GatherMathExpr`][midstack.compiler.analog.rewrite.canonicalize.GatherMathExpr],
        [`OperatorDistribute`][midstack.compiler.analog.rewrite.canonicalize.OperatorDistribute],
        [`ProperOrder`][midstack.compiler.analog.rewrite.canonicalize.ProperOrder]

    Example:
        - X@(Y*Z) => fail
        - X@Y => pass
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
    Checks whether all MathExpr have been gathered (i.e. basically checks whether
    there is any scalar multiplication within a term)

    Args:
        model (VisitableBaseModel): The rule only verifies [`Operator`][midstack.interface.analog.operator.Operator] in Analog level

    Returns:
        model (VisitableBaseMode): unchanged

    Assumptions:
        OperatorDistribute
        [`OperatorDistribute`][midstack.compiler.analog.rewrite.canonicalize.OperatorDistribute]

    Example:
        - X@(1*Z) => fail
        - 1*(X@Z) => pass
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
    Checks for incomplete distribution of Operators

    Args:
        model (VisitableBaseModel): The rule only verifies [`Operator`][midstack.interface.analog.operator.Operator] in Analog level

    Returns:
        model (VisitableBaseMode): unchanged

    Assumptions:
        None

    Example:
        - X@(Y+Z) => fail
        - X@Y + X@Z => pass
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
    Checks whether all Operators are ProperOrdered according to how they are bracketed
    Please see example for clarification

    Args:
        model (VisitableBaseModel): The rule only verifies [`Operator`][midstack.interface.analog.operator.Operator] in Analog level

    Returns:
        model (VisitableBaseMode): unchanged

    Assumptions:
        None

    Example:
        - X@(Y@Z) => fail
        - (X@Y)@Z => pass
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
    Checks if there is any ladder Identity present in ladder multiplication

    Args:
        model (VisitableBaseModel): The rule only verifies [`Operator`][midstack.interface.analog.operator.Operator] in Analog level

    Returns:
        model (VisitableBaseMode): unchanged

    Assumptions:
        OperatorDistribute
        [`OperatorDistribute`][midstack.compiler.analog.rewrite.canonicalize.OperatorDistribute]

    Example:
        - A*J*C => fail
        - A*C => pass
    """

    def map_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, Identity) or isinstance(model.op2, Identity):
            raise CanonicalFormError("Prune Identity is not complete")
        pass


class CanVerGatherPauli(RewriteRule):
    """
    Checks whether pauli and ladder have been separated.

    Args:
        model (VisitableBaseModel): The rule only verifies [`Operator`][midstack.interface.analog.operator.Operator] in Analog level

    Returns:
        model (VisitableBaseMode): unchanged

    Assumptions:
        [`GatherMathExpr`][midstack.compiler.analog.rewrite.canonicalize.GatherMathExpr],
        [`OperatorDistribute`][midstack.compiler.analog.rewrite.canonicalize.OperatorDistribute],
        [`ProperOrder`][midstack.compiler.analog.rewrite.canonicalize.ProperOrder],
        [`PauliAlgebra`][midstack.compiler.analog.rewrite.canonicalize.PauliAlgebra]

    Example:
        - X@A@Y => fail
        - X@Y@A => pass
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
    Checks whether the ladder operations are in normal order

    Args:
        model (VisitableBaseModel): The rule only verifies [`Operator`][midstack.interface.analog.operator.Operator] in Analog level

    Returns:
        model (VisitableBaseMode): unchanged

    Assumptions:
        OperatorDistribute, GatherMathExpr, ProperOrder, PauliAlgebra, PruneIdentity
        [`GatherMathExpr`][midstack.compiler.analog.rewrite.canonicalize.GatherMathExpr],
        [`OperatorDistribute`][midstack.compiler.analog.rewrite.canonicalize.OperatorDistribute],
        [`ProperOrder`][midstack.compiler.analog.rewrite.canonicalize.ProperOrder],
        [`PauliAlgebra`][midstack.compiler.analog.rewrite.canonicalize.PauliAlgebra],
        [`PruneIdentity`][midstack.compiler.analog.rewrite.canonicalize.PruneIdentity]


    Example:
        - A*C => fail
        - C*A => pass
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
    Checks whether operators are in sorted order according to TermIndex.
    Please see example for further clarification

    Args:
        model (VisitableBaseModel): The rule only verifies [`Operator`][midstack.interface.analog.operator.Operator] in Analog level

    Returns:
        model (VisitableBaseMode): unchanged

    Assumptions:
        [`GatherMathExpr`][midstack.compiler.analog.rewrite.canonicalize.GatherMathExpr],
        [`OperatorDistribute`][midstack.compiler.analog.rewrite.canonicalize.OperatorDistribute],
        [`ProperOrder`][midstack.compiler.analog.rewrite.canonicalize.ProperOrder],
        [`GatherPauli`][midstack.compiler.analog.rewrite.canonicalize.GatherPauli],
        [`NormalOrder`][midstack.compiler.analog.rewrite.canonicalize.NormalOrder],
        [`PruneIdentity`][midstack.compiler.analog.rewrite.canonicalize.PruneIdentity]

    Example:
        - X + I => fail
        - I + X => pass
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
    Checks whether all terms have a scalar multiplication.

    Args:
        model (VisitableBaseModel): The rule only verifies [`Operator`][midstack.interface.analog.operator.Operator] in Analog level

    Returns:
        model (VisitableBaseMode): unchanged

    Assumptions:
        [`GatherMathExpr`][midstack.compiler.analog.rewrite.canonicalize.GatherMathExpr],
        [`OperatorDistribute`][midstack.compiler.analog.rewrite.canonicalize.OperatorDistribute],
        [`ProperOrder`][midstack.compiler.analog.rewrite.canonicalize.ProperOrder],
        [`GatherPauli`][midstack.compiler.analog.rewrite.canonicalize.GatherPauli]

    Example:
        - X + 2*Y => fail
        - 1*X + 2*Y => pass
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
