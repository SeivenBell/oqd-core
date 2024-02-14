from typing import Any, Union

########################################################################################

from quantumion.interface.analog import *

from quantumion.compiler.analog.base import AnalogCircuitTransformer

########################################################################################


class GatherMathExpr(AnalogCircuitTransformer):
    def _visit(self, model: Any) -> Any:
        if isinstance(model, (OpMul, OpKron)):
            return self._visit_OpMulKron(model)
        if isinstance(model, (OpAdd, OpSub)):
            return self._visit_OpAddSub(model)
        if isinstance(model, Operator):
            return model
        raise TypeError

    def visit_OpScalarMul(self, model: OpScalarMul):
        if isinstance(model.op, OpScalarMul):
            return model.expr * model.op.expr * self.visit(model.op.op)
        return model.expr * self.visit(model.op)

    def _visit_OpMulKron(self, model: Union[OpMul, OpKron]):
        if isinstance(model.op1, OpScalarMul) and isinstance(model.op2, OpScalarMul):
            return (
                model.op1.expr
                * model.op2.expr
                * self.visit(model.__class__(op1=model.op1.op, op2=model.op2.op))
            )
        if isinstance(model.op1, OpScalarMul):
            return model.op1.expr * self.visit(
                model.__class__(op1=model.op1.op, op2=model.op2)
            )
        if isinstance(model.op2, OpScalarMul):
            return model.op2.expr * self.visit(
                model.__class__(op1=model.op1, op2=model.op2.op)
            )
        return model.__class__(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def _visit_OpAddSub(self, model: Union[OpAdd, OpSub]):
        return model.__class__(op1=self.visit(model.op1), op2=self.visit(model.op2))
