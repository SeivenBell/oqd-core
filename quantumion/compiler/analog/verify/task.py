from quantumion.interface.analog import AnalogGate
from quantumion.compiler.rule import RewriteRule
from quantumion.compiler.analog.passes.analysis import analysis_canonical_hamiltonian_dim
from quantumion.backend.metric import Expectation

__all__ = [
    "VerifyAnalogCircuitDim",
    "VerifyAnalogArgsDim",
]

class VerifyAnalogCircuitDim(RewriteRule):
    def __init__(self, n_qreg, n_qmode):
        super().__init__()
        self._dim: tuple = (n_qreg, n_qmode)

    def map_AnalogGate(self, model: AnalogGate):
        assert self._dim == analysis_canonical_hamiltonian_dim(model.hamiltonian)


class VerifyAnalogArgsDim(RewriteRule):
    def __init__(self, n_qreg, n_qmode):
        super().__init__()
        self._dim: tuple = (n_qreg, n_qmode)

    def map_Expectation(self, model: Expectation):
        assert self._dim == analysis_canonical_hamiltonian_dim(model.operator)
