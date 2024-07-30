from typing import Any, Union

########################################################################################

from quantumion.interface.analog import *
from quantumion.interface.math import MathExpr
from quantumion.compilerv2.rule import RewriteRule
from quantumion.compilerv2.walk import Post, Pre
from quantumion.compilerv2.analog.utils import get_canonical_hamiltonian_dim
from rich import print as pprint


## write an analysis to get the info and then assign


class AssignAnalogIRDim(RewriteRule):
    def __init__(self):
        super().__init__()
        self.dim = None
                

    
    def map_AnalogCircuit(self, model: AnalogCircuit):
        model.n_qreg = self.dim[0]
        model.n_qmode = self.dim[1]
        return model
    def map_AnalogGate(self, model):
        if self.dim is None:
            self.dim = get_canonical_hamiltonian_dim(model.hamiltonian)       
        elif self.dim != get_canonical_hamiltonian_dim(model.hamiltonian):
            raise Exception 



if __name__ == '__main__':
    from quantumion.compiler.analog.base import *
    X, Y, Z, I, A, C, LI = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()
    ac = AnalogCircuit()
    ac.evolve(gate=AnalogGate(hamiltonian=1*(X@X) + 1*(Y@Y@(A*C))), duration=1)
    ac.evolve(gate = AnalogGate(hamiltonian=1*(Y@Y@(A*C))), duration=1)
    pprint(Post(AssignAnalogIRDim())(ac))
