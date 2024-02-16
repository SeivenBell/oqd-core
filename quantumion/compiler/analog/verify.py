from typing import Union, Any

########################################################################################

from quantumion.interface.analog import *

from quantumion.compiler.analog.base import AnalogCircuitTransformer, PrintOperator

########################################################################################


class VerifyHilbertSpace(AnalogCircuitTransformer):
    def _visit(self, model):
        if isinstance(model, (OperatorAdd, OperatorSub, OperatorMul)):
            return self.visit_OperatorAddSubMul(model)
        raise TypeError

    def visit_Pauli(self, model):
        return (1, 0)

    def visit_Ladder(self, model):
        return (0, 1)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        return self.visit(model.op)

    def visit_OperatorAddSubMul(
        self, model: Union[OperatorAdd, OperatorSub, OperatorMul]
    ):
        space1 = self.visit(model.op1)
        space2 = self.visit(model.op2)

        assert space1 == space2, (
            "\nInconsistent Hilbert space between:"
            + f"\n\t{model.op1.accept(PrintOperator())}"
            + f"\n\t{model.op2.accept(PrintOperator())}"
        )
        return space1

    def visit_OperatorKron(self, model: OperatorKron):
        space1 = self.visit(model.op1)
        space2 = self.visit(model.op2)

        space = (space1[0] + space2[0], space1[1] + space2[1])
        return space
