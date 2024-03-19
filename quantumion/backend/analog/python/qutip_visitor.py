from quantumion.compiler.analog.base import AnalogInterfaceTransformer, AnalogCircuitTransformer
from quantumion.interface.analog.operator import *
from quantumion.interface.analog.operations import *
import qutip as qt
from rich import print as pprint

__all__ = [
    "QutipBackendTransformer",
    "QutipConvertTransformer",
]
class QutipExperiment(AnalogInterfaceTransformer):
    """Transformer to run an experiment (maybe use visitor?)"""

class QutipConvertTransformer(AnalogCircuitTransformer):

    def visit_PauliI(self, model: PauliI):
        return qt.qeye(2)

    def visit_PauliX(self, model: PauliX):
        return qt.sigmax()
    
    def visit_PauliY(self, model: PauliY):
        return qt.sigmay()

    def visit_PauliZ(self, model: PauliZ):
        return qt.sigmaz()
    
    def visit_OperatorKron(self, model: OperatorKron):
        return qt.tensor(self.visit(model.op1), self.visit(model.op2))

class QutipBackendTransformer(AnalogInterfaceTransformer):
    """convert task to QutipObj without running (maybe use visitor?)
    Basically compiles down to qutip object using transformers.
    """
    def __init__(self):
        super().__init__()

    def visit_AnalogCircuit(self, model: AnalogCircuit):
        return self.visit(model.sequence)
    
    def visit_Evolve(self, model: Evolve):
        return (self.visit(model.gate),model.duration)

    def visit_AnalogGate(self, model: AnalogGate):
        return self.visit(model.hamiltonian)
    
    def visit_OperatorAdd(self, model: OperatorAdd):        
        op = self.visit(model.op1)
        op.append(self.visit(model.op2)[0])
        return op
    
    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        return [(model.op, model.expr)]

if __name__ == "__main__":
    X, Y, Z, I, A, C, J = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()