from quantumion.interface.analog.operations import *
from quantumion.compiler.analog.canonicalize import *
from quantumion.interface.analog.operator import *
from quantumion.compiler.analog.base import AnalogInterfaceTransformer
from typing import Union
    
class RegisterInformation(AnalogInterfaceTransformer):
    """
    Assumes all hamiltonians in AnalogSystem are in canonical form
    """
    def _visit(self, model):
        if isinstance(model, (OperatorAdd, OperatorSub, OperatorMul)):
            return self.visit_OperatorAddSubMul(model)
        else:
            return super()._visit(model=model)

    def visit_AnalogGate(self, model: AnalogGate):
        if model.hamiltonian ==  None:
            raise Exception("Hamiltonian not defined")
        #visit_out = self.visit(model.hamiltonian)
        #model.n_qreg, model.n_qmode = visit_out[0], visit_out[1]
        #return model
        return self.visit(model.hamiltonian)
    
    def visit_AnalogCircuit(self, model: AnalogCircuit):
        visit_out = self.visit(model.sequence)
        for elem in visit_out:
            if elem != visit_out[0]:
                raise Exception("Incorrect Dimensions between AnalogGates")
        n_qreg, n_qmode = visit_out[0]
        return AnalogCircuit(
            sequence = model.sequence,
            n_qreg = n_qreg,
            n_qmode = n_qmode,
            definitions = model.definitions,
            qreg = model.qreg,
            qmode = model.qmode
        )
    
    def visit_Evolve(self, model: Evolve):
        return self.visit(model.gate)
    
    def visit_Pauli(self, model):
        return (1, 0)

    def visit_Ladder(self, model):
        return (0, 1)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        return self.visit(model.op)

    def visit_OperatorAddSubMul(self, model: Union[OperatorAdd, OperatorSub, OperatorMul]):
        return self.visit(model.op2)

    def visit_OperatorKron(self, model: OperatorKron):
        space1 = self.visit(model.op1)
        space2 = self.visit(model.op2)
        return (space1[0] + space2[0], space1[1] + space2[1])
