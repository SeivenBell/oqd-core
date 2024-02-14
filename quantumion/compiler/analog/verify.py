from typing import Union, Any

########################################################################################

from quantumion.interface.analog import *

from quantumion.compiler.analog.base import AnalogCircuitTransformer, PrintOperator

########################################################################################


class VerifyHilbertSpace(AnalogCircuitTransformer):
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
        space1 = self.visit(model.op1)
        space2 = self.visit(model.op2)

        assert space1 == space2, (
            "\nInconsistent Hilbert space between:"
            + f"\n\t{model.op1.accept(PrintOperator())}"
            + f"\n\t{model.op2.accept(PrintOperator())}"
        )
        return space1

    def visit_OpKron(self, model: OpKron):
        space1 = self.visit(model.op1)
        space2 = self.visit(model.op2)

        space = (space1[0] + space2[0], space1[1] + space2[1])
        return space
