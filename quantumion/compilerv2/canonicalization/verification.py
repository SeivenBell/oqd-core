from quantumion.compilerv2.rewriter import *
from quantumion.compilerv2.rule import *
from quantumion.compilerv2.walk import *
from quantumion.compilerv2.canonicalization.utils import term_index_dim
from quantumion.compilerv2.canonicalization.rules import TermIndex
from quantumion.interface.math import *
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
        if isinstance(model.op1, Pauli) and isinstance(model.op2, Pauli):
            raise CanonicalFormError("Incomplete Pauli Algebra")
        elif isinstance(model.op1, Pauli) and isinstance(model.op2, Ladder):
            raise CanonicalFormError("Incorrect Ladder and Pauli multiplication")
        elif isinstance(model.op1, Ladder) and isinstance(model.op2, Pauli):
            raise CanonicalFormError("Incorrect Ladder and Pauli multiplication")
        pass

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
    
class CanVerOperatorDistribute(RewriteRule):
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


    def _OperatorMulKron(self, model: (OperatorMul, OperatorKron)):
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
    """Assumptions:
    None
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
    """Assumptions:
    >>> Distributed
    """

    def map_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, Identity) or isinstance(model.op2, Identity):
            raise CanonicalFormError("Prune Identity is not complete")
        pass

class CanVerGatherPauli(RewriteRule):
    """Assumptions:
    >>> Distributed, Gathered and then proper ordered and PauliAlgebra
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
    """Assumptions:
    >>> Distributed, Gathered and then proper ordered and PauliAlgebra, PruneIdentity
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
    Assumptions: GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli, NormalOrder
                 PruneIdentity
    """
    def map_OperatorAdd(self, model: OperatorAdd):
        term2 = PostConversion(TermIndex())(model.op2)
        if isinstance(model.op1, OperatorAdd):
            term1 = PostConversion(TermIndex())(model.op1.op2)
        else:
            term1 = PostConversion(TermIndex())(model.op1)
        if term_index_dim(term1) != term_index_dim(term2):
            raise CanonicalFormError("Incorrect dimension of hilbert space")
        if term1 > term2:
            raise CanonicalFormError("Terms are not in sorted order")
        elif term1 == term2:
            raise CanonicalFormError("Duplicate terms present")
        pass

class CanVerScaleTerm(RewriteRule):
    """
    Assumptions: 
    >>> GatherMathExpr, OperatorDistribute, ProperOrder, GatherPauli, NormalOrder, PruneIdentity
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
        if isinstance(model.op2, OperatorScalarMul) and isinstance(model.op1, Union[OperatorScalarMul, OperatorAdd]):
            pass
        else:
            raise CanonicalFormError("some operators between addition are not scaled properly")