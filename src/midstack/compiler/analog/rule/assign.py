from typing import Any, Union

########################################################################################

from midstack.interface.analog import AnalogCircuit
from midstack.compiler.rule import RewriteRule
from midstack.compiler.analog.passes.analysis import analysis_canonical_hamiltonian_dim

########################################################################################

__all__ = [
    "AssignAnalogIRDim",
]

########################################################################################


class AssignAnalogIRDim(RewriteRule):
    """
    RewriteRule which gets the dimensions from analysis pass
    analysis_canonical_hamiltonian_dim and then inserts the dimension in the Analog IR

    Args:
        model (VisitableBaseModel):
               The rule only modifies [`AnalogCircuit`][midstack.interface.analog.operations.AnalogCircuit] in Analog level

    Returns:
        model  (VisitableBaseModel):

    Assumptions:
        - All [`Operator`][midstack.interface.analog.operator.Operator] inside  [`AnalogCircuit`][midstack.interface.analog.operations.AnalogCircuit] must be in canonical form
    """

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
