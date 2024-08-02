from typing import Any, Union
from quantumion.interface.analog import AnalogCircuit, AnalogGate
from quantumion.compilerv2.rule import RewriteRule
from quantumion.compilerv2.analog.utils import get_canonical_hamiltonian_dim
from quantumion.backend.metric import Expectation


class AssignAnalogIRDim(RewriteRule):
    def __init__(self):
        super().__init__()
        self.dim: Union[tuple, None] = None

    def map_AnalogCircuit(self, model: AnalogCircuit):
        model.n_qreg = self.dim[0]
        model.n_qmode = self.dim[1]
        return model
    def map_AnalogGate(self, model):
        if self.dim is None:
            self.dim = get_canonical_hamiltonian_dim(model.hamiltonian)       
        elif self.dim != get_canonical_hamiltonian_dim(model.hamiltonian):
            raise Exception
        
class VerifyAnalogCircuitDim(RewriteRule):
    def __init__(self, n_qreg, n_qmode):
        super().__init__()
        self._dim: tuple = (n_qreg, n_qmode)

    def map_AnalogGate(self, model: AnalogGate):
        assert self._dim == get_canonical_hamiltonian_dim(model.hamiltonian)


class VerifyAnalogArgsDim(RewriteRule):
    def __init__(self, n_qreg, n_qmode):
        super().__init__()
        self._dim: tuple = (n_qreg, n_qmode)

    def map_Expectation(self, model: Expectation):
        assert self._dim == get_canonical_hamiltonian_dim(model.operator)