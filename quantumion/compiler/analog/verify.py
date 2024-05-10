from typing import Union, Any

########################################################################################

from quantumion.interface.analog import *
from quantumion.interface.base import VisitableBaseModel

from quantumion.compiler.analog.base import *
from quantumion.compiler.analog.error import *
from quantumion.compiler.analog.canonicalize import *

########################################################################################

__all__ = [
    "VerifyHilbertSpace",
    "CanonicalizationVerificationOperator",
    "CanonicalizationVerificationOperatorDistribute",
    "CanonicalizationVerificationGatherMathExpr",
    "CanonicalizationVerificationProperOrder",
    "CanonicalizationVerificationPauliAlgebra",
    "CanonicalizationVerificationGatherPauli",
    "CanonicalizationVerificationNormalOrder",
    "CanonicalizationVerificationPruneIdentity",
    "CanonicalizationVerificationSortedOrder",
    "CanonicalizationVerificationScaleTerms",
]

########################################################################################


class CanonicalizationVerificationOperator(AnalogCircuitVisitor):
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

    def _visit(self, model: Any) -> Any:
        if isinstance(model, (Operator)):
            pass
        elif isinstance(model, VisitableBaseModel):
            self.reset()
        super()._visit(model)

    def visit_OperatorAdd(self, model: OperatorAdd):

        try:
            model.accept(VerifyHilbertSpace())
        except AssertionError:
            raise CanonicalFormError(
                "Hilbert Space Verification failed. Please check for dimension errors"
            )

        if isinstance(model.op2, model.__class__):
            raise CanonicalFormError("Incorrect Proper Ordering in Addition")

        if not (
            isinstance(model.op1, (OperatorAdd, OperatorScalarMul))
            and isinstance(model.op2, (OperatorAdd, OperatorScalarMul))
        ):
            raise CanonicalFormError("Some terms are not scaled in the operator")

        if isinstance(model.op1, self.add_allowed_ops) and isinstance(
            model.op2, self.add_allowed_ops
        ):
            if TermIndex().visit(model.op1) > TermIndex().visit(model.op2):
                raise CanonicalFormError(
                    "TermIndex {} and {} are not in sorted order".format(
                        TermIndex().visit(model.op1), TermIndex().visit(model.op2)
                    )
                )
            elif (
                TermIndex().visit(model.op1) in self._term_indices
                or TermIndex().visit(model.op1) in self._term_indices
                or TermIndex().visit(model.op1) == TermIndex().visit(model.op2)
            ):
                raise CanonicalFormError("Duplicate terms present")

        if self._current_term_index == None:
            self._current_term_index = TermIndex().visit(model.op2)
            self._term_indices.append(self._current_term_index)

        elif TermIndex().visit(model.op2) > self._current_term_index:
            raise CanonicalFormError(
                "TermIndex {} and {} are not in sorted order".format(
                    TermIndex().visit(model.op2), self._current_term_index
                )
            )
        elif TermIndex().visit(model.op2) in self._term_indices:
            raise CanonicalFormError("Duplicate terms of {} present".format(model.op2))
        else:
            self._current_term_index = TermIndex().visit(model.op2)
            self._term_indices.append(self._current_term_index)

        if isinstance(model.op1, OperatorAdd) and isinstance(
            model.op2, self.add_allowed_ops
        ):
            self.visit(model.op1)
            self.visit(model.op2)
        elif isinstance(model.op1, self.add_allowed_ops) and isinstance(
            model.op2, self.add_allowed_ops
        ):
            self.visit(model.op1)
            self.visit(model.op2)
        else:
            raise CanonicalFormError("Incorrect canonical addition")

    def visit_OperatorMul(self, model: OperatorMul):
        _allowed_prod_ops = Union[
            Ladder,
            OperatorMul,
        ]
        """
        OpMul should not have OpKron and Anhilitation or something else. It should not have opkron at all
        """
        if isinstance(model.op1, Annihilation) or isinstance(model.op2, Annihilation):
            if self.creation_tracker:
                raise CanonicalFormError("Ladders are not in Normal order")

        if isinstance(model.op1, Identity) or isinstance(model.op2, Identity):
            raise CanonicalFormError(
                "Idenitities should not be present in Normal order"
            )

        if isinstance(model.op2, model.__class__):
            raise CanonicalFormError(
                "Incorrect Proper Ordering in Operator Multiplication"
            )

        if not (
            isinstance(model.op1, _allowed_prod_ops)
            and isinstance(model.op2, _allowed_prod_ops)
        ):
            raise CanonicalFormError(
                "Incorrect canonical Operator multiplication"
            )  # pauli algebra not fully applied

        if isinstance(model.op1, OperatorMul):  # check op2 ladder
            if isinstance(model.op2, Creation):
                self.creation_tracker = True
            self.visit(model=model.op1)

        if isinstance(model.op1, Ladder) and isinstance(model.op2, Ladder):  # Terminal
            if isinstance(model.op1, Annihilation) and isinstance(model.op2, Creation):
                raise CanonicalFormError("Ladders are not in Normal order")
            self.creation_tracker = False

    def visit_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op2, model.__class__):
            raise CanonicalFormError("Incorrect Proper Ordering in Operator kron")

        if isinstance(model.op1, (OperatorMul, OperatorKron)):
            self.visit(model=model.op1)

        if isinstance(
            model.op2, (OperatorMul)
        ):  # ProperOrder: no need and raise error for not proper order
            self.visit(model=model.op2)

        if not (
            isinstance(model.op1, self.allowed_ops)
            and isinstance(model.op2, self.allowed_ops)
        ):  # terminal
            raise CanonicalFormError("Incorrect canonical kron")

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(
            model.op, self.allowed_ops
        ):  # paulis and ladders are needed for edge cases (i.e. for single register systems)
            self.visit(model=model.op)
        else:
            raise CanonicalFormError(
                "Incorrect canonical scalar operator multiplication"
            )

    def visit_OperatorSub(self, model: OperatorSub):
        if isinstance(model, OperatorSub):
            raise CanonicalFormError("Subtraction of terms present")


class VerifyHilbertSpace(AnalogCircuitVisitor):
    """
    We should not have:
    def visit_AnalogGate(self, model: AnalogGate):
        self.visit(model.hamiltonian)
    This is because, then the default visitor will not be activated and thus, the global space dimension will
    not be recorded.
    """

    def __init__(self):
        super().__init__()
        self.global_space = None

    def reset(self):
        self.global_space = None

    def _visit(self, model):
        if isinstance(model, (OperatorAdd, OperatorSub, OperatorMul)):
            self.visit_OperatorAddSubMul(model)
        elif isinstance(model, VisitableBaseModel) and not isinstance(model, Operator):
            for key in model.__dict__.keys():
                self.visit(getattr(model, key))
                if not isinstance(model, Operator) and isinstance(
                    getattr(model, key), Operator
                ):
                    if self.global_space == None:
                        self.global_space = self.space_temp
                    elif self.global_space != self.space_temp:
                        raise ValueError(
                            "Different Hilbert spaces encountered. Please check the dimensions of Args and gates."
                        )
        else:
            super(self.__class__, self)._visit(model)

    def visit_Pauli(self, model: Pauli):
        self.space_temp = (1, 0)

    def visit_Ladder(self, model: Ladder):
        self.space_temp = (0, 1)

    def visit_OperatorKron(self, model: OperatorKron):

        self.visit(model.op1)
        op1_space = self.space_temp

        self.visit(model.op2)
        op2_space = self.space_temp

        self.space_temp = tuple(map(sum, zip(op1_space, op2_space)))

    def visit_OperatorAddSubMul(
        self, model: Union[OperatorAdd, OperatorSub, OperatorMul]
    ):
        self.visit(model.op1)
        left = self.space_temp

        self.visit(model.op2)
        right = self.space_temp

        assert left == right, (
            "\nInconsistent Hilbert space between:"
            + f"\n\t{model.op1.accept(PrintOperator())}"
            + f"\n\t{model.op2.accept(PrintOperator())}"
        )


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
        else:
            self.visit(model.op1)
            self.visit(model.op2)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if not (isinstance(model.op, self.allowed_ops)):
            raise CanonicalFormError(
                "Scalar multiplication of operators not simplified fully"
            )
        else:
            self.visit(model=model.op)

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
        if isinstance(model.op1, OperatorScalarMul) or isinstance(
            model.op2, OperatorScalarMul
        ):
            raise CanonicalFormError("Incomplete Gather Math Expression")
        else:
            self.visit(model.op1)
            self.visit(model.op2)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, OperatorScalarMul):
            raise CanonicalFormError(
                "Incomplete scalar multiplications after GatherMathExpression"
            )
        else:
            self.visit(model=model.op)


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
            raise CanonicalFormError(
                "Incorrect Proper Ordering (for scalar multiplication)"
            )
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
        elif isinstance(model, Operator):
            super(self.__class__, self)._visit(model)
        elif isinstance(model, VisitableBaseModel):
            self.reset()
            super(self.__class__, self)._visit(model)
        else:
            super(self.__class__, self)._visit(model)

    def visit_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op2, Pauli):
            self.pauli_tracker = True
            self.visit(model.op1)
        if isinstance(model.op1, (Ladder, OperatorMul)) or isinstance(
            model.op2, (Ladder, OperatorMul)
        ):
            self.visit(
                model.op2
            )  # left tree contains @ and right tree contains multiplications (right is more complicated than left). test both to see which cases fail
            if self.pauli_tracker:
                raise CanonicalFormError("Incorrect GatherPauli")
            self.visit(model.op1)

    def visit_OperatorMul(
        self, model: OperatorMul
    ):  # extra precaution to ensure pauli algebra is not present for GatherPauli
        if isinstance(model.op1, Pauli) or isinstance(model.op2, Pauli):
            raise CanonicalFormError(
                "Pauli Algbebra incomplete or Pauli * Ladder present"
            )
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
        if isinstance(model, (Operator)):
            pass
        elif isinstance(model, VisitableBaseModel):
            self.reset()
        super()._visit(model)

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

    def visit_OperatorAddSubMulKron(
        self, model: Union[OperatorAdd, OperatorSub, OperatorMul, OperatorKron]
    ):
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

    def _visit(self, model: Any) -> Any:
        if isinstance(model, (Operator)):
            pass
        elif isinstance(model, VisitableBaseModel):
            self.reset()
        super()._visit(model)

    def visit_OperatorAdd(self, model: OperatorAdd):
        if isinstance(model.op1, self._allowed_nodes) and isinstance(
            model.op2, self._allowed_nodes
        ):
            if TermIndex().visit(model.op1) > TermIndex().visit(model.op2):
                raise CanonicalFormError(
                    "TermIndex {} and {} are not in sorted order".format(
                        TermIndex().visit(model.op1), TermIndex().visit(model.op2)
                    )
                )
            elif (
                TermIndex().visit(model.op1) in self._term_indices
                or TermIndex().visit(model.op1) in self._term_indices
                or TermIndex().visit(model.op1) == TermIndex().visit(model.op2)
            ):
                raise CanonicalFormError("Duplicate terms present")

        if self._current_term_index == None:
            self._current_term_index = TermIndex().visit(model.op2)
            self._term_indices.append(self._current_term_index)

        elif TermIndex().visit(model.op2) > self._current_term_index:
            raise CanonicalFormError(
                "TermIndex {} and {} are not in sorted order".format(
                    TermIndex().visit(model.op2), self._current_term_index
                )
            )
        elif TermIndex().visit(model.op2) in self._term_indices:
            raise CanonicalFormError("Duplicate terms of {} present".format(model.op2))
        else:
            self._current_term_index = TermIndex().visit(model.op2)
            self._term_indices.append(self._current_term_index)

        self.visit(model.op1)


class CanonicalizationVerificationScaleTerms(AnalogCircuitVisitor):
    def _visit(self, model: Any):
        if isinstance(model, Operator):
            return self.visit_OperatorNotOpAdd(model)
        return super(self.__class__, self)._visit(model)

    def visit_OperatorAdd(self, model: OperatorAdd):
        self.visit(model.op2)
        self.visit(model.op1)

    def visit_OperatorNotOpAdd(self, model: Any):
        if not isinstance(model, OperatorScalarMul):
            raise CanonicalFormError("Term {} is not scaled".format(model))
