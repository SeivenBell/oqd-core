from typing import Union, Any

########################################################################################

from quantumion.interface.analog import *

from quantumion.compiler.analog.base import AnalogCircuitTransform

########################################################################################


class VerifyHilbertSpace(AnalogCircuitTransform):
    def _visit(self, model):
        if isinstance(model, Pauli):
            return (1, 0)
        if isinstance(model, Ladder):
            return (0, 1)
        if isinstance(model, (OpAdd, OpSub, OpMul)):
            return self._visit_OpAddSubMul(model)
        raise TypeError

    def visit_OpScalarMul(self, model: OpScalarMul):
        return self.visit(model.op)

    def _visit_OpAddSubMul(self, model: Union[OpAdd, OpSub, OpMul]):
        dim1 = self.visit(model.op1)
        dim2 = self.visit(model.op2)

        assert dim1 == dim2
        return dim1

    def visit_OpKron(self, model: OpKron):
        dim1 = self.visit(model.op1)
        dim2 = self.visit(model.op2)

        dim = (dim1[0] + dim2[0], dim1[1] + dim2[1])
        return dim
