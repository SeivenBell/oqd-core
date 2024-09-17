from oqd_compiler_infrastructure import RewriteRule

########################################################################################

from ....interface.analog import AnalogGate
from ..passes.analysis import analysis_canonical_hamiltonian_dim
from ....backend.metric import Expectation

########################################################################################

__all__ = [
    "VerifyAnalogCircuitDim",
    "VerifyAnalogArgsDim",
]

########################################################################################


class VerifyAnalogCircuitDim(RewriteRule):
    """
    Checks  whether hilbert space dimensions are consistent between  [`AnalogGate`][midstack.interface.analog.operations.AnalogGate] objects.
    and whether they match the n_qreg and n_qmode given as input.

    Args:
        model (VisitableBaseModel):
            The rule only verifies [`AnalogCircuit`][midstack.interface.analog.operations.AnalogCircuit] in Analog level

    Returns:
        model (VisitableBaseModel): unchanged

    Assumptions:
        All [`Operator`][midstack.interface.analog.operator.Operator] inside  [`AnalogCircuit`][midstack.interface.analog.operations.AnalogCircuit] are canonicalized
    """

    def __init__(self, n_qreg, n_qmode):
        super().__init__()
        self._dim: tuple = (n_qreg, n_qmode)

    def map_AnalogGate(self, model: AnalogGate):
        assert self._dim == analysis_canonical_hamiltonian_dim(
            model.hamiltonian
        ), "Inconsistent Hilbert space dimension between Analog Gates"


class VerifyAnalogArgsDim(RewriteRule):
    """
    Checks whether hilbert space dimensions are consistent between Expectation in args
    and whether they match the n_qreg and n_qmode given as input.

    Args:
        model (VisitableBaseModel):
            The rule only verfies Expectation inside TaskArgsAnalog in Analog layer

    Returns:
        model (VisitableBaseModel): unchanged

    Assumptions:
        All [`Operator`][midstack.interface.analog.operator.Operator] inside  [`AnalogCircuit`][midstack.interface.analog.operations.AnalogCircuit] are canonicalized
    """

    def __init__(self, n_qreg, n_qmode):
        super().__init__()
        self._dim: tuple = (n_qreg, n_qmode)

    def map_Expectation(self, model: Expectation):
        assert self._dim == analysis_canonical_hamiltonian_dim(
            model.operator
        ), "Inconsistent Hilbert space dimension in Expectation metric"
