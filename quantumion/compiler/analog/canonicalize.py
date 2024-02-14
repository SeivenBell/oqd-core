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


########################################################################################


class ProperKronOrder(AnalogCircuitTransformer):
    def visit_OpKron(self, model: OpKron):
        if isinstance(model.op1, OpKron):
            return OpKron(
                op1=self.visit(model.op1.op1),
                op2=OpKron(op1=self.visit(model.op1.op2), op2=self.visit(model.op2)),
            )
        return OpKron(op1=self.visit(model.op1), op2=self.visit(model.op2))


class SeparatePauliLadder(AnalogCircuitTransformer):
    def visit_OpKron(self, model: OpKron):
        print(model.op1)
        if isinstance(model.op1, Ladder):
            if isinstance(model.op2, Pauli):
                return OpKron(
                    op1=model.op2,
                    op2=model.op1,
                )
            if isinstance(model.op2, OpKron):
                return OpKron(
                    op1=model.op2.op1, op2=OpKron(op1=model.op1, op2=model.op2.op2)
                )
        return OpKron(op1=self.visit(model.op1), op2=self.visit(model.op2))


class DeNestOpMulKron(AnalogCircuitTransformer):
    def visit_OpMul(self, model: OpMul):
        if isinstance(model.op1, (OpAdd, OpSub)):
            return model.op1.__class__(
                op1=self.visit(OpMul(op1=model.op1.op1, op2=model.op2)),
                op2=self.visit(OpMul(op1=model.op1.op2, op2=model.op2)),
            )
        if isinstance(model.op2, (OpAdd, OpSub)):
            return model.op2.__class__(
                op1=self.visit(OpMul(op1=model.op1, op2=model.op2.op1)),
                op2=self.visit(OpMul(op1=model.op1, op2=model.op2.op2)),
            )
        return OpMul(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def visit_OpKron(self, model: OpKron):
        if isinstance(model.op1, (OpAdd, OpSub, OpMul)):
            return model.op1.__class__(
                op1=self.visit(OpKron(op1=model.op1.op1, op2=model.op2)),
                op2=self.visit(OpKron(op1=model.op1.op2, op2=model.op2)),
            )
        if isinstance(model.op2, (OpAdd, OpSub, OpMul)):
            return model.op2.__class__(
                op1=self.visit(OpKron(op1=model.op1, op2=model.op2.op1)),
                op2=self.visit(OpKron(op1=model.op1, op2=model.op2.op2)),
            )
        return OpKron(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def visit_OpScalarMul(self, model: OpScalarMul):
        if isinstance(model.op, (OpAdd, OpSub)):
            return model.op.__class__(
                op1=OpScalarMul(op=self.visit(model.op.op1), expr=model.expr),
                op2=OpScalarMul(op=self.visit(model.op.op2), expr=model.expr),
            )
        return OpScalarMul(op=self.visit(model.op), expr=model.expr)
