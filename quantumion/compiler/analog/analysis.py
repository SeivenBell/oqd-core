from quantumion.interface.analog.operations import *
from quantumion.compiler.analog.canonicalize import *
from quantumion.interface.analog.operator import *
from quantumion.compiler.analog.base import AnalogInterfaceTransformer
from quantumion.compiler.analog.verify import VerifyHilbertSpace
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
        self.visit(model.hamiltonian)
        return model
    
    def visit_AnalogCircuit(self, model: AnalogCircuit):
        """
        Note that we assume VerifyHilbertSpace has passed on model as without VerifyHilbertSpace passing,
        this visitor will produce incorrect results. As an additional safety check we again run VerifyHilbertSpace
        before visiting AnalogCircuit node
        """
        try:
            model.accept(VerifyHilbertSpace())
        except:
            raise ValueError("Different Hilbert spaces encountered during Hilbert Space Verification")
        for idx, instruction in enumerate(model.sequence):
            self.visit(instruction)
            if idx == 0:
                first_space_dim = self.space_temp 
            elif self.space_temp != first_space_dim:
                raise ValueError("Different Hilbert spaces encountered")
        n_qreg, n_qmode = self.space_temp
        return AnalogCircuit(
            sequence = model.sequence,
            n_qreg = n_qreg,
            n_qmode = n_qmode,
            definitions = model.definitions,
            qreg = model.qreg,
            qmode = model.qmode
        )
    
    def visit_Evolve(self, model: Evolve):
        self.visit(model.gate)
        return model
    
    def visit_Pauli(self, model):
        self.space_temp = (1,0)
        return model

    def visit_Ladder(self, model):
        self.space_temp = (0,1)
        return model

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        self.visit(model.op)
        return model

    def visit_OperatorAddSubMul(self, model: Union[OperatorAdd, OperatorSub, OperatorMul]):
        self.visit(model.op2)
        return model

    def visit_OperatorKron(self, model: OperatorKron):
        self.visit(model.op1)
        op1_space = self.space_temp

        self.visit(model.op2)
        op2_space = self.space_temp

        self.space_temp = tuple(map(sum, zip(op1_space, op2_space)))
        return model

