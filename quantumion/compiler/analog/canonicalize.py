from typing import Any, Union

########################################################################################

from quantumion.interface.math import MathNum, MathImag, MathAdd, MathExpr
from quantumion.interface.analog import *
from quantumion.compiler.analog.verify import *

from quantumion.compiler.analog.base import AnalogCircuitTransformer, AnalogCircuitVisitor

########################################################################################

__all__ = [
    "PruneIdentity",
    "PauliAlgebra",
    "GatherMathExpr",
    "GatherPauli",
    "OperatorDistribute",
    "ProperOrder",
    "NormalOrder",
    "TermIndex",
    "SortedOrder",
    "CanonicalizationVerificationOperator",
    "CanonicalFormError",
    "CanonicalizationVerificationOperatorDistribute",
    "CanonicalizationVerificationGatherMathExpr",
    "CanonicalizationVerificationProperOrder",
    "CanonicalizationVerificationPauliAlgebra",
    "CanonicalizationVerificationGatherPauli",
    "CanonicalizationVerificationNormalOrder",
    "CanonicalizationVerificationPruneIdentity",
    "CanonicalizationVerificationSortedOrder",
]

########################################################################################


class PruneIdentity(AnalogCircuitTransformer):
    def visit_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, (Identity, PauliI)):
            return self.visit(model.op2)
        if isinstance(model.op2, (Identity, PauliI)):
            return self.visit(model.op1)
        return OperatorMul(op1=self.visit(model.op1), op2=self.visit(model.op2))


class PauliAlgebra(AnalogCircuitTransformer):
    def visit_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, Pauli) and isinstance(model.op2, Pauli):
            if isinstance(model.op1, PauliI):
                return self.visit(model.op2)
            if isinstance(model.op2, PauliI):
                return self.visit(model.op1)
            if model.op1 == model.op2:
                return PauliI()
            if isinstance(model.op1, PauliX) and isinstance(model.op2, PauliY):
                return OperatorScalarMul(op=PauliZ(), expr=MathImag())
            if isinstance(model.op1, PauliY) and isinstance(model.op2, PauliZ):
                return OperatorScalarMul(op=PauliX(), expr=MathImag())
            if isinstance(model.op1, PauliZ) and isinstance(model.op2, PauliX):
                return OperatorScalarMul(op=PauliY(), expr=MathImag())
            return OperatorScalarMul(
                op=self.visit(OperatorMul(op1=model.op2, op2=model.op1)),
                expr=MathNum(value=-1),
            )
        return OperatorMul(op1=self.visit(model.op1), op2=self.visit(model.op2))


########################################################################################


class GatherMathExpr(AnalogCircuitTransformer):
    def _visit(self, model: Any) -> Any:
        if isinstance(model, (OperatorMul, OperatorKron)):
            return self.visit_OperatorMulKron(model)
        if isinstance(model, (OperatorAdd, OperatorSub)):
            return self.visit_OperatorAddSub(model)
        if isinstance(model, Operator):
            return model
        raise TypeError

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, OperatorScalarMul):
            return model.expr * model.op.expr * self.visit(model.op.op)
        return model.expr * self.visit(model.op)

    def visit_OperatorMulKron(self, model: Union[OperatorMul, OperatorKron]):
        if isinstance(model.op1, OperatorScalarMul) and isinstance(
            model.op2, OperatorScalarMul
        ):
            return (
                model.op1.expr
                * model.op2.expr
                * self.visit(model.__class__(op1=model.op1.op, op2=model.op2.op))
            )
        if isinstance(model.op1, OperatorScalarMul):
            return model.op1.expr * self.visit(
                model.__class__(op1=model.op1.op, op2=model.op2)
            )
        if isinstance(model.op2, OperatorScalarMul):
            return model.op2.expr * self.visit(
                model.__class__(op1=model.op1, op2=model.op2.op)
            )
        return model.__class__(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def visit_OperatorAddSub(self, model: Union[OperatorAdd, OperatorSub]):
        return model.__class__(op1=self.visit(model.op1), op2=self.visit(model.op2))


class GatherPauli(AnalogCircuitTransformer):
    def visit_OperatorKron(self, model: OperatorKron):
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
        return OperatorKron(op1=self.visit(model.op1), op2=self.visit(model.op2))


########################################################################################


class OperatorDistribute(AnalogCircuitTransformer):
    def visit_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, (OperatorAdd, OperatorSub)):
            return model.op1.__class__(
                op1=self.visit(OperatorMul(op1=model.op1.op1, op2=model.op2)),
                op2=self.visit(OperatorMul(op1=model.op1.op2, op2=model.op2)),
            )
        if isinstance(model.op2, (OperatorAdd, OperatorSub)):
            return model.op2.__class__(
                op1=self.visit(OperatorMul(op1=model.op1, op2=model.op2.op1)),
                op2=self.visit(OperatorMul(op1=model.op1, op2=model.op2.op2)),
            )
        if isinstance(model.op1, (OperatorKron)) and isinstance(
            model.op2, (OperatorKron)
        ):
            return OperatorKron(
                op1=OperatorMul(op1=model.op1.op1, op2=model.op2.op1),
                op2=OperatorMul(op1=model.op1.op2, op2=model.op2.op2),
            )
        return OperatorMul(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def visit_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op1, (OperatorAdd, OperatorSub)):
            return model.op1.__class__(
                op1=self.visit(OperatorKron(op1=model.op1.op1, op2=model.op2)),
                op2=self.visit(OperatorKron(op1=model.op1.op2, op2=model.op2)),
            )
        if isinstance(model.op2, (OperatorAdd, OperatorSub)):
            return model.op2.__class__(
                op1=self.visit(OperatorKron(op1=model.op1, op2=model.op2.op1)),
                op2=self.visit(OperatorKron(op1=model.op1, op2=model.op2.op2)),
            )
        return OperatorKron(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, (OperatorAdd, OperatorSub)):
            return model.op.__class__(
                op1=OperatorScalarMul(op=self.visit(model.op.op1), expr=model.expr),
                op2=OperatorScalarMul(op=self.visit(model.op.op2), expr=model.expr),
            )
        return OperatorScalarMul(op=self.visit(model.op), expr=model.expr)

    def visit_OperatorSub(self, model: OperatorSub):
        return OperatorAdd(
            op1=self.visit(model.op1),
            op2=OperatorScalarMul(op=self.visit(model.op2), expr=MathNum(value=-1)),
        )


########################################################################################


class ProperOrder(AnalogCircuitTransformer):
    def _visit(self, model: Any):
        if isinstance(model, (OperatorAdd, OperatorMul, OperatorKron)):
            return self.visit_OperatorAddMulKron(model)
        return super(self.__class__, self)._visit(model)

    def visit_OperatorAddMulKron(
        self, model: Union[OperatorAdd, OperatorMul, OperatorKron]
    ):
        if isinstance(model.op2, model.__class__):
            return model.__class__(
                op1=model.__class__(
                    op1=self.visit(model.op1), op2=self.visit(model.op2.op1)
                ),
                op2=self.visit(model.op2.op2),
            )
        return model.__class__(op1=self.visit(model.op1), op2=self.visit(model.op2))


########################################################################################


class NormalOrder(AnalogCircuitTransformer):
    def visit_OperatorMul(self, model: OperatorMul):
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
                    op1=self.visit(model.op1.op1),
                    op2=self.visit(OperatorMul(op1=model.op1.op2, op2=model.op2)),
                )
        return OperatorMul(op1=self.visit(model.op1), op2=self.visit(model.op2))


########################################################################################


class TermIndex(AnalogCircuitTransformer):
    def visit_PauliI(self, model: PauliI):
        return 0

    def visit_PauliX(self, model: PauliX):
        return 1

    def visit_PauliY(self, model: PauliY):
        return 2

    def visit_PauliZ(self, model: PauliZ):
        return 3

    def visit_Identity(self, model: Identity):
        return (0, 0)

    def visit_Annihilation(self, model: Annihilation):
        return (1, 0)

    def visit_Creation(self, model: Annihilation):
        return (1, 1)

    def visit_OperatorAdd(self, model: OperatorAdd):
        term1 = (
            self.visit(model.op1)
            if isinstance(model.op1, OperatorAdd)
            else [self.visit(model.op1)]
        )
        term2 = self.visit(model.op2)
        return term1 + [term2]

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        term = self.visit(model.op)
        return term

    def visit_OperatorMul(self, model: OperatorMul):
        if not(isinstance(model.op1, (Ladder, model.__class__)) and isinstance(model.op2, (Ladder, model.__class__))):
            raise CanonicalFormError("More simplification required for Term Index")
        term1 = self.visit(model.op1)
        term2 = self.visit(model.op2)
        return (term1[0] + term2[0], term1[1] + term2[1])

    def visit_OperatorKron(self, model: OperatorKron):
        term1 = self.visit(model.op1)
        term1 = term1 if isinstance(term1, list) else [term1]
        term2 = self.visit(model.op2)
        term2 = term2 if isinstance(term2, list) else [term2]
        return term1 + term2


class SortedOrder(AnalogCircuitTransformer):
    def visit_OperatorAdd(self, model: OperatorAdd):
        if isinstance(model.op1, OperatorAdd):
            term1 = TermIndex().visit(model.op1.op2)
            term2 = TermIndex().visit(model.op2)

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
                    op1=self.visit(model.op1.op1),
                    op2=OperatorScalarMul(
                        op=op, expr=MathAdd(expr1=expr1, expr2=expr2)
                    ),
                )

            elif term1 > term2:
                return OperatorAdd(
                    op1=self.visit(OperatorAdd(op1=model.op1.op1, op2=model.op2)),
                    op2=model.op1.op2,
                )

            elif term1 < term2:
                return OperatorAdd(op1=self.visit(model.op1), op2=model.op2)

        else:
            term1 = TermIndex().visit(model.op1)
            term2 = TermIndex().visit(model.op2)

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

class CanonicalFormError(Exception):
    """
    Error class for canonical form (maybe we need it to put it elsewhere)
    """
    pass

class CanonicalizationVerificationOperator(AnalogCircuitVisitor):
    ## assuming VerifyHilbertSpace runs without issues
    def __init__(self):
        super().__init__()
        self.allowed_ops = Union[
            OperatorTerminal,
            OperatorMul,
            OperatorKron,
        ]

        self.add_allowed_ops = Union[
            OperatorTerminal,
            OperatorMul,
            OperatorKron,
            OperatorScalarMul,
        ]
        self.creation_tracker = False
        self._term_indices = []
        self._current_term_index = None

    def reset(self):
        self.creation_tracker = False
        self._term_indices = []
        self._current_term_index = None

    def visit_OperatorAdd(self, model: OperatorAdd):

        try:
            model.accept(VerifyHilbertSpace())
        except AssertionError:
            raise CanonicalFormError("Hilbert Space Verification failed. Please check for dimension errors")

        if isinstance(model.op2, model.__class__):
            raise CanonicalFormError("Incorrect Proper Ordering in Addition")

        if isinstance(model.op1, self.add_allowed_ops) and isinstance(model.op2, self.add_allowed_ops):
            if TermIndex().visit(model.op1) > TermIndex().visit(model.op2):
                raise CanonicalFormError("TermIndex {} and {} are not in sorted order".format(TermIndex().visit(model.op1), TermIndex().visit(model.op2)))
            elif TermIndex().visit(model.op1) in self._term_indices or TermIndex().visit(model.op1) in self._term_indices or TermIndex().visit(model.op1) == TermIndex().visit(model.op2):
                raise CanonicalFormError("Duplicate terms present")
        
        if self._current_term_index == None:
            self._current_term_index = TermIndex().visit(model.op2)
            self._term_indices.append(self._current_term_index)

        elif TermIndex().visit(model.op2) > self._current_term_index:
            raise CanonicalFormError("TermIndex {} and {} are not in sorted order".format(TermIndex().visit(model.op2), self._current_term_index))
        elif TermIndex().visit(model.op2) in self._term_indices:
            raise CanonicalFormError("Duplicate terms of {} present".format(model.op2))
        else:
            self._current_term_index = TermIndex().visit(model.op2)
            self._term_indices.append(self._current_term_index)
    
        if isinstance(model.op1, OperatorAdd) and isinstance(model.op2, self.add_allowed_ops):
            self.visit(model.op1)
            self.visit(model.op2)
        elif isinstance(model.op1, self.add_allowed_ops) and isinstance(model.op2, self.add_allowed_ops):
            self.visit(model.op1)
            self.visit(model.op2)
        else:
            raise CanonicalFormError("Incorrect canonical addition")
        
    def visit_OperatorMul(self, model: OperatorMul):
        _allowed_prod_ops = Union[Ladder,
                                  OperatorMul,
                                  ]
        """
        OpMul should not have OpKron and Anhilitation or something else. It should not have opkron at all
        """
        if (isinstance(model.op1, Annihilation) or isinstance(model.op2, Annihilation)):
            if self.creation_tracker:
                raise CanonicalFormError("Ladders are not in Normal order")

        if isinstance(model.op1, Identity) or isinstance(model.op2, Identity):
            raise CanonicalFormError("Idenitities should not be present in Normal order")

        if isinstance(model.op2, model.__class__):
            raise CanonicalFormError("Incorrect Proper Ordering in Operator Multiplication")

        if not (isinstance(model.op1, _allowed_prod_ops) and isinstance(model.op2, _allowed_prod_ops)):
            raise CanonicalFormError("Incorrect canonical Operator multiplication") # pauli algebra not fully applied
        
        if isinstance(model.op1, OperatorMul): # check op2 ladder
            if isinstance(model.op2, Creation):
                self.creation_tracker = True
            self.visit(model=model.op1)

        if isinstance(model.op1, Ladder) and isinstance(model.op2, Ladder): # Terminal
            if isinstance(model.op1, Annihilation) and isinstance(model.op2, Creation):
                raise CanonicalFormError("Ladders are not in Normal order")
            self.creation_tracker = False

    def visit_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op2, model.__class__):
            raise CanonicalFormError("Incorrect Proper Ordering in Operator kron")

        if isinstance(model.op1, (OperatorMul, OperatorKron)):
            self.visit(model=model.op1)
        
        if isinstance(model.op2, (OperatorMul)): # ProperOrder: no need and raise error for not proper order
            self.visit(model=model.op2)
        
        if not(isinstance(model.op1, self.allowed_ops) and isinstance(model.op2, self.allowed_ops)): # terminal
            raise CanonicalFormError("Incorrect canonical kron")
        
    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, self.allowed_ops): # paulis and ladders are needed for edge cases (i.e. for single register systems)
            self.visit(model = model.op)
        else:
            raise CanonicalFormError("Incorrect canonical scalar operator multiplication")
        
    def visit_OperatorSub(self, model: OperatorSub):
        if isinstance(model, OperatorSub):
            raise CanonicalFormError("Subtraction of terms present")


class CanonicalizationVerificationOperatorDistribute(AnalogCircuitVisitor):
    def __init__(self):
        super().__init__()
        self.allowed_ops = Union[
                OperatorTerminal,
                Ladder,
                OperatorMul,
                OperatorScalarMul,
                OperatorKron,
            ]
    def _visit(self, model: Any) -> Any:
        if isinstance(model, (OperatorMul, OperatorKron)):
            self.visit_OperatorMulKron(model)
        else:
            super(self.__class__, self)._visit(model)
    
    def visit_OperatorMulKron(self, model: (OperatorMul, OperatorKron)):
        if isinstance(model, OperatorMul) and isinstance(model.op1, OperatorKron) and isinstance(model.op2, OperatorKron):
            raise CanonicalFormError("Incomplete Operator Distribution (multiplication of OperatorKron present)")
        elif not(isinstance(model.op1, self.allowed_ops) and isinstance(model.op2, self.allowed_ops)):
            raise CanonicalFormError("Incomplete Operator Distribution")
        else:
            self.visit(model.op1)
            self.visit(model.op2)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if not(isinstance(model.op, self.allowed_ops)):
            raise CanonicalFormError("Scalar multiplication of operators not simplified fully")
        else:
            self.visit(model = model.op)

    def visit_OperatorSub(self, model: OperatorSub):
        if isinstance(model, OperatorSub):
            raise CanonicalFormError("Subtraction of terms present")

class CanonicalizationVerificationGatherMathExpr(AnalogCircuitVisitor):
    """Assuming that OperatorDistribute has already been fully ran"""
    def _visit(self, model: Any) -> Any:
        if isinstance(model, (OperatorMul, OperatorKron)):
            self.visit_OperatorMulKron(model)
        else:
            super(self.__class__, self)._visit(model)
    
    def visit_OperatorMulKron(self, model: (OperatorMul, OperatorKron)):
        if isinstance(model.op1, OperatorScalarMul) or isinstance(model.op2, OperatorScalarMul):
            raise CanonicalFormError("Incomplete Gather Math Expression")
        else:
            self.visit(model.op1)
            self.visit(model.op2)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, OperatorScalarMul):
            raise CanonicalFormError("Incomplete scalar multiplications after GatherMathExpression")
        else:
            self.visit(model = model.op)

class CanonicalizationVerificationProperOrder(AnalogCircuitVisitor):
    """Assumptions:
        None
    """
    def _visit(self, model: Any) -> Any:
        if isinstance(model, (OperatorAdd, OperatorMul, OperatorKron)):
            self.visit_OperatorAddMulKron(model)
        else:
            super(self.__class__, self)._visit(model)

    def visit_OperatorAddMulKron(self, model: (OperatorAdd, OperatorMul, OperatorKron)):
        if isinstance(model.op2, model.__class__):
            raise CanonicalFormError("Incorrect Proper Ordering")
        else:
            self.visit(model.op1)
            self.visit(model.op2)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, model.__class__):
            raise CanonicalFormError("Incorrect Proper Ordering (for scalar multiplication)")
        else:
            self.visit(model.op)

class CanonicalizationVerificationPauliAlgebra(AnalogCircuitVisitor):
    """
    Assumptions:
    Distributed, Gathered and then proper ordered. Then MatMul is done on the set of operators.
    """
    def visit_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, Pauli) and isinstance(model.op2, Pauli):
            raise CanonicalFormError("Incomplete Pauli Algebra")
        else:
            self.visit(model.op1)
            self.visit(model.op2)

class CanonicalizationVerificationGatherPauli(AnalogCircuitVisitor):
    """Assumptions:
    >>> Distributed, Gathered and then proper ordered and PauliAlgebra
    """
    def __init__(self):
        super().__init__()
        self.pauli_tracker = False

    def reset(self):
        self.pauli_tracker = False

    def _visit(self, model: Any) -> Any:
        if isinstance(model, (OperatorAdd, OperatorSub)):
            self.visit_OperatorAddSub(model)
        else:
            super(self.__class__, self)._visit(model)

    def visit_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op2, Pauli):
            self.pauli_tracker = True
            self.visit(model.op1)
        if (isinstance(model.op1, (Ladder, OperatorMul)) or isinstance(model.op2, (Ladder, OperatorMul))):
            self.visit(model.op2) # left tree contains @ and right tree contains multiplications (right is more complicated than left). test both to see which cases fail
            if self.pauli_tracker:
                raise CanonicalFormError("Incorrect GatherPauli")
            self.visit(model.op1)

    def visit_OperatorMul(self, model: OperatorMul): # extra precaution to ensure pauli algebra is not present for GatherPauli
        if isinstance(model.op1, Pauli) or isinstance(model.op2, Pauli):
            raise CanonicalFormError("Pauli Algbebra incomplete or Pauli * Ladder present")
        self.visit(model.op1)
        self.visit(model.op2)

    def visit_OperatorAddSub(self, model: Union[OperatorAdd, OperatorSub]):
        self.pauli_tracker = False
        self.visit(model.op1)
        self.pauli_tracker = False
        self.visit(model.op2)
        
class CanonicalizationVerificationNormalOrder(AnalogCircuitVisitor):
    """Assumptions:
    >>> Distributed, Gathered and then proper ordered, PauliAlgebra and GatherPauli
    """
    def __init__(self):
        super().__init__()
        self.creation_tracker = False

    def reset(self):
        self.creation_tracker = False

    def _visit(self, model: Any) -> Any:
        if isinstance(model, (OperatorAdd, OperatorSub, OperatorMul, OperatorKron)):
            self.visit_OperatorAddSubMulKron(model)
        else:
            super(self.__class__, self)._visit(model)

    def visit_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op2, Creation):
            self.creation_tracker = True
            self.visit(model.op1)
        if isinstance(model.op1, Annihilation) and isinstance(model.op2, Creation):
            raise CanonicalFormError("Terminal Ladders are not in Normal order")
        if isinstance(model.op1, Annihilation) or isinstance(model.op2, Annihilation):
            if self.creation_tracker:
                raise CanonicalFormError("Ladders are not in Normal order")
        self.visit(model.op2)
        self.visit(model.op1)

    def visit_OperatorAddSubMulKron(self, model: Union[OperatorAdd, OperatorSub, OperatorMul, OperatorKron]):
        self.creation_tracker = False
        self.visit(model.op1)
        self.creation_tracker = False
        self.visit(model.op2)

class CanonicalizationVerificationPruneIdentity(AnalogCircuitVisitor):
    """Assumptions:
    >>> Distributed, Gathered
    """
    def visit_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, Identity) or isinstance(model.op2, Identity):
            raise CanonicalFormError("Prune Identity is not complete")
        self.visit(model.op1)
        self.visit(model.op2)

class CanonicalizationVerificationSortedOrder(AnalogCircuitVisitor):
    """Assumptions:
    Ideally this should be the very last step of the process as you should be sorting right before completion
    """
    def __init__(self):
        self._current_term_index = None
        self._term_indices = []
        self._allowed_nodes = Union[
            OperatorTerminal,
            OperatorMul,
            OperatorKron,
            OperatorScalarMul,
        ]
        super().__init__()

    def reset(self):
        self._current_term_index = None
        self._term_indices = []

    def visit_OperatorAdd(self, model: OperatorAdd):
        if isinstance(model.op1, self._allowed_nodes) and isinstance(model.op2, self._allowed_nodes):
            if TermIndex().visit(model.op1) > TermIndex().visit(model.op2):
                raise CanonicalFormError("TermIndex {} and {} are not in sorted order".format(TermIndex().visit(model.op1), TermIndex().visit(model.op2)))
            elif TermIndex().visit(model.op1) in self._term_indices or TermIndex().visit(model.op1) in self._term_indices or TermIndex().visit(model.op1) == TermIndex().visit(model.op2):
                raise CanonicalFormError("Duplicate terms present")
        
        if self._current_term_index == None:
            self._current_term_index = TermIndex().visit(model.op2)
            self._term_indices.append(self._current_term_index)

        elif TermIndex().visit(model.op2) > self._current_term_index:
            raise CanonicalFormError("TermIndex {} and {} are not in sorted order".format(TermIndex().visit(model.op2), self._current_term_index))
        elif TermIndex().visit(model.op2) in self._term_indices:
            raise CanonicalFormError("Duplicate terms of {} present".format(model.op2))
        else:
            self._current_term_index = TermIndex().visit(model.op2)
            self._term_indices.append(self._current_term_index)

        self.visit(model.op1)

if __name__ == '__main__':
    from rich import print as pprint
    from quantumion.compiler.analog import *
    X, Y, Z, I = PauliX(), PauliY(), PauliZ(), PauliI()
    A, C, LI =  Annihilation(), Creation(), Identity()