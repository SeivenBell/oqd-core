from typing import Union

########################################################################################

from midstack.compiler.rule import RewriteRule
from midstack.interface.analog import *

__all__ = [
    "VerifyHilberSpaceDim",
]


class VerifyHilberSpaceDim(RewriteRule):
    """
    Checks whether the hilbert spaces are correct between additions.

    Args:
        model (VisitableBaseModel):
            The rule only verifies [`Operator`][midstack.interface.analog.operator.Operator] in Analog level

    Returns:
        model (VisitableBaseModel): unchanged

    Assumptions:
        [`GatherMathExpr`][midstack.compiler.analog.rewrite.canonicalize.GatherMathExpr],
        [`OperatorDistribute`][midstack.compiler.analog.rewrite.canonicalize.OperatorDistribute],
        [`ProperOrder`][midstack.compiler.analog.rewrite.canonicalize.ProperOrder],
        [`PauliAlgebra`][midstack.compiler.analog.rewrite.canonicalize.PauliAlgebra]

    Example:
        - X@A + Y@Z => fail
        - X@Y + Y@Z => pass
    """

    def __init__(self):
        super().__init__()
        self._dim = (0, 0)
        self._term_dim = None
        self._final_add_term = False

    def _reset(self):
        self._dim = (0, 0)
        self._term_dim = None
        self._final_add_term = False

    def map_AnalogGate(self, model):
        self._reset()

    def map_Expectation(self, model):
        self._reset()

    def _get_dim(self, model):
        if isinstance(model, Pauli):
            return (1, 0)
        elif isinstance(model, Union[Ladder, OperatorMul]):
            return (0, 1)

    def map_OperatorKron(self, model):
        new = self._get_dim(model.op2)
        self._dim = (self._dim[0] + new[0], self._dim[1] + new[1])
        if isinstance(model.op1, Union[OperatorTerminal, OperatorMul]):
            new = self._get_dim(model.op1)
            self._dim = (self._dim[0] + new[0], self._dim[1] + new[1])
            if self._final_add_term:
                assert self._term_dim == self._dim, "Incorrect Hilbert space dimension"

    def map_OperatorAdd(self, model):
        new = self._dim
        if isinstance(model.op2, Union[OperatorMul, OperatorTerminal]):
            new = self._get_dim(model.op2)
        elif isinstance(model.op2, OperatorScalarMul):
            if isinstance(model.op2.op, Union[OperatorTerminal, OperatorMul]):
                new = self._get_dim(model.op2.op)

        if self._term_dim == None:
            self._term_dim = new
        else:
            assert self._term_dim == new, "Incorrect Hilbert space dimension"

        if isinstance(model.op1, Union[OperatorTerminal, OperatorMul]):
            assert self._term_dim == self._get_dim(
                model.op1
            ), "Incorrect Hilbert space dimension"
        elif isinstance(model.op1, OperatorScalarMul):
            if isinstance(model.op1.op, Union[OperatorTerminal, OperatorMul]):
                assert self._term_dim == self._get_dim(
                    model.op1.op
                ), "Incorrect Hilbert space dimension"

        if not isinstance(model.op1, OperatorAdd):
            self._final_add_term = True
        self._dim = (0, 0)
