from quantumion.interface.analog import AnalogGate
from quantumion.compiler.rule import RewriteRule
from quantumion.compiler.analog.passes.analysis import analysis_canonical_hamiltonian_dim
from quantumion.backend.metric import Expectation

__all__ = [
    "VerifyAnalogCircuitDim",
    "VerifyAnalogArgsDim",
]

class VerifyAnalogCircuitDim(RewriteRule):
    """
    This checks whether hilbert space dimensions are consistent between AnalogGates
    and whether they match the n_qreg and n_qmode given as input
    """
    def __init__(self, n_qreg, n_qmode):
        super().__init__()
        self._dim: tuple = (n_qreg, n_qmode)

    def map_AnalogGate(self, model: AnalogGate):
        assert self._dim == analysis_canonical_hamiltonian_dim(model.hamiltonian), "Inconsistent Hilbert space dimension between Analog Gates"


class VerifyAnalogArgsDim(RewriteRule):
    """
    This checks whether hilbert space dimensions are consistent between Expectation in args
    and whether they match the n_qreg and n_qmode given as input
    """
    def __init__(self, n_qreg, n_qmode):
        super().__init__()
        self._dim: tuple = (n_qreg, n_qmode)

    def map_Expectation(self, model: Expectation):
        assert self._dim == analysis_canonical_hamiltonian_dim(model.operator), "Inconsistent Hilbert space dimension in Expectation metric"
