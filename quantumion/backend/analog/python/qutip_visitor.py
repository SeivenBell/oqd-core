from quantumion.compiler.analog.base import AnalogInterfaceTransformer
from quantumion.interface.analog.operator import *
from quantumion.interface.analog.operations import *
from rich import print as pprint

__all__ = [
    "QutipBackendTransformer",
]
class QutipExperiment(AnalogInterfaceTransformer):
    """Transformer to run an experiment (maybe use visitor?)"""

class QutipBackendTransformer(AnalogInterfaceTransformer):
    """convert task to QutipObj without running (maybe use visitor?)
    Basically compiles down to qutip object using transformers.
    """
    def __init__(self):
        self.qt_array = []
        super().__init__()

    def visit_AnalogCircuit(self, model: AnalogCircuit):
        return self.visit(model.sequence)
    
    def visit_Evolve(self, model: Evolve):
        self.qt_array = []
        return self.visit(model.gate) 

    def visit_AnalogGate(self, model: AnalogGate):
        return self.visit(model.hamiltonian)
    
    def visit_OperatorAdd(self, model: OperatorAdd):
        self.visit(model.op2)
        self.visit(model.op1)
        return self.qt_array
        # coefficient_op2 = model.op2.expr
        # op_op2 = model.op2.op

        # self.qt_array.append([op_op2, coefficient_op2])
        # self.visit(model.op2)
        # self.visit(model.op1)

        # if not isinstance(model.op1, OperatorAdd):
        #     coefficient_op1 = model.op1.expr
        #     op_op1 = model.op1.op
        #     self.qt_array.append([op_op1, coefficient_op1])
        # else:
        #     self.visit(model.op1)
        #return self.qt_array 
        # if isinstance(model.op1, OperatorAdd):
        #     return self.visit(model.op1)
        # else:
        #     self.visit(model.op1)
    
    
    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        self.qt_array.append([model.op, model.expr])
        return self.qt_array

if __name__ == "__main__":
    X, Y, Z, I, A, C, J = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()