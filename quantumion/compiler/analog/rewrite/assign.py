from typing import Any, Union

########################################################################################

from quantumion.interface.analog import AnalogCircuit
from quantumion.compiler.rule import RewriteRule
from quantumion.compiler.analog.passes.analysis import analysis_canonical_hamiltonian_dim

########################################################################################

__all__ = [
    "AssignAnalogIRDim",
]

########################################################################################


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
            self.dim = analysis_canonical_hamiltonian_dim(model.hamiltonian)
        elif self.dim != analysis_canonical_hamiltonian_dim(model.hamiltonian):
            raise Exception
