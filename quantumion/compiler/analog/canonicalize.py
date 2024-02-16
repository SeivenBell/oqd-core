from typing import Any, Union

########################################################################################

from quantumion.interface.math import MathNum, MathImag, MathAdd
from quantumion.interface.analog import *

from quantumion.compiler.analog.base import AnalogCircuitTransformer


########################################################################################


class PruneIdentity(AnalogCircuitTransformer):
    def visit_OpMul(self, model: OpMul):
        if isinstance(model.op1, (Identity, PauliI)):
            return self.visit(model.op2)
        if isinstance(model.op2, (Identity, PauliI)):
            return self.visit(model.op1)
        return OpMul(op1=self.visit(model.op1), op2=self.visit(model.op2))


class PauliAlgebra(AnalogCircuitTransformer):
    def visit_OpMul(self, model: OpMul):
        if isinstance(model.op1, Pauli) and isinstance(model.op2, Pauli):
            if isinstance(model.op1, PauliI):
                return self.visit(model.op2)
            if isinstance(model.op2, PauliI):
                return self.visit(model.op1)
            if model.op1 == model.op2:
                return PauliI()
            if isinstance(model.op1, PauliX) and isinstance(model.op2, PauliY):
                return OpScalarMul(op=PauliZ(), expr=MathImag())
            if isinstance(model.op1, PauliY) and isinstance(model.op2, PauliZ):
                return OpScalarMul(op=PauliX(), expr=MathImag())
            if isinstance(model.op1, PauliZ) and isinstance(model.op2, PauliX):
                return OpScalarMul(op=PauliY(), expr=MathImag())
            return OpScalarMul(
                op=self.visit(OpMul(op1=model.op2, op2=model.op1)),
                expr=MathNum(value=-1),
            )
        return OpMul(op1=self.visit(model.op1), op2=self.visit(model.op2))


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


class GatherPauli(AnalogCircuitTransformer):
    def visit_OpKron(self, model: OpKron):
        if isinstance(model.op2, Pauli):
            if isinstance(model.op1, Ladder):
                return OpKron(
                    op1=model.op2,
                    op2=model.op1,
                )
            if isinstance(model.op1, OpKron) and isinstance(
                model.op1.op2, Union[Ladder, OpMul]
            ):
                return OpKron(
                    op1=OpKron(op1=model.op1.op1, op2=model.op2), op2=model.op1.op2
                )
        return OpKron(op1=self.visit(model.op1), op2=self.visit(model.op2))


########################################################################################


class Distribute(AnalogCircuitTransformer):
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
        if isinstance(model.op1, (OpKron)) and isinstance(model.op2, (OpKron)):
            return OpKron(
                op1=OpMul(op1=model.op1.op1, op2=model.op2.op1),
                op2=OpMul(op1=model.op1.op2, op2=model.op2.op2),
            )
        return OpMul(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def visit_OpKron(self, model: OpKron):
        if isinstance(model.op1, (OpAdd, OpSub)):
            return model.op1.__class__(
                op1=self.visit(OpKron(op1=model.op1.op1, op2=model.op2)),
                op2=self.visit(OpKron(op1=model.op1.op2, op2=model.op2)),
            )
        if isinstance(model.op2, (OpAdd, OpSub)):
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

    def visit_OpSub(self, model: OpSub):
        return OpAdd(
            op1=self.visit(model.op1),
            op2=OpScalarMul(op=self.visit(model.op2), expr=MathNum(value=-1)),
        )


########################################################################################


class ProperOrder(AnalogCircuitTransformer):
    def visit_OpKron(self, model: OpKron):
        if isinstance(model.op2, OpKron):
            return OpKron(
                op1=OpKron(op1=self.visit(model.op1), op2=self.visit(model.op2.op1)),
                op2=self.visit(model.op2.op2),
            )
        return OpKron(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def visit_OpMul(self, model: OpMul):
        if isinstance(model.op2, OpMul):
            return OpMul(
                op1=OpMul(op1=self.visit(model.op1), op2=self.visit(model.op2.op1)),
                op2=self.visit(model.op2.op2),
            )
        return OpMul(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def visit_OpAdd(self, model: OpAdd):
        if isinstance(model.op2, OpAdd):
            return OpAdd(
                op1=OpAdd(op1=self.visit(model.op1), op2=self.visit(model.op2.op1)),
                op2=self.visit(model.op2.op2),
            )
        return OpAdd(op1=self.visit(model.op1), op2=self.visit(model.op2))


########################################################################################


class NormalOrder(AnalogCircuitTransformer):
    def visit_OpMul(self, model: OpMul):
        if isinstance(model.op2, Creation):
            if isinstance(model.op1, Annihilation):
                return OpSub(op1=OpMul(op1=model.op2, op2=model.op1), op2=Identity())
            if isinstance(model.op1, OpMul) and isinstance(model.op1.op2, Annihilation):
                return OpMul(
                    op1=self.visit(model.op1.op1),
                    op2=OpSub(
                        op1=OpMul(op1=model.op2, op2=model.op1.op2), op2=Identity()
                    ),
                )
            if isinstance(model.op1, Identity):
                return OpMul(op1=model.op2, op2=model.op1)
            if isinstance(model.op1, OpMul) and isinstance(model.op1.op2, Identity):
                return OpMul(
                    op1=self.visit(model.op1.op1),
                    op2=OpMul(op1=model.op2, op2=model.op1.op2),
                )
        return OpMul(op1=self.visit(model.op1), op2=self.visit(model.op2))


########################################################################################


class TermIndex(AnalogCircuitTransformer):
    def _visit(self, model):
        if isinstance(model, Ladder):
            return (0, 1)

    def visit_PauliI(self, model: PauliI):
        return [0]

    def visit_PauliX(self, model: PauliX):
        return [1]

    def visit_PauliY(self, model: PauliY):
        return [2]

    def visit_PauliZ(self, model: PauliZ):
        return [3]

    def visit_Identity(self, model: Identity):
        return [0, 0]

    def visit_Annihilation(self, model: Annihilation):
        return [1, 0]

    def visit_Creation(self, model: Annihilation):
        return [1, 1]

    def visit_OpAdd(self, model: OpAdd):
        term1 = (
            self.visit(model.op1)
            if isinstance(model.op1, OpAdd)
            else [self.visit(model.op1)]
        )
        term2 = self.visit(model.op2)
        return term1 + [term2]

    def visit_OpScalarMul(self, model: OpScalarMul):
        term = self.visit(model.op)
        return term

    def visit_OpMul(self, model: OpMul):
        term1 = self.visit(model.op1)
        term2 = self.visit(model.op2)
        return [term1[0] + term2[0], term1[1] + term2[1]]

    def visit_OpKron(self, model: OpKron):
        term1 = self.visit(model.op1)
        term2 = self.visit(model.op2)
        return term1 + term2


class SortedOrder(AnalogCircuitTransformer):
    def visit_OpAdd(self, model: OpAdd):
        if isinstance(model.op1, OpAdd):
            term1 = TermIndex().visit(model.op1.op2)
            term2 = TermIndex().visit(model.op2)

            if term1 == term2:
                expr1 = (
                    model.op1.op2.expr
                    if isinstance(model.op1.op2, OpScalarMul)
                    else MathNum(value=1)
                )
                expr2 = (
                    model.op2.expr
                    if isinstance(model.op2, OpScalarMul)
                    else MathNum(value=1)
                )
                op = model.op2.op if isinstance(model.op2, OpScalarMul) else model.op2
                return OpAdd(
                    op1=self.visit(model.op1.op1),
                    op2=OpScalarMul(op=op, expr=MathAdd(expr1=expr1, expr2=expr2)),
                )

            i = 0
            while True:
                if term1[i] > term2[i]:
                    return OpAdd(
                        op1=self.visit(OpAdd(op1=model.op1.op1, op2=model.op2)),
                        op2=model.op1.op2,
                    )
                if term1[i] < term2[i]:
                    return OpAdd(op1=self.visit(model.op1), op2=model.op2)
                if term1[i] == term2[i]:
                    i += 1
                    continue

        term1 = TermIndex().visit(model.op1)
        term2 = TermIndex().visit(model.op2)

        if term1 == term2:
            expr1 = (
                model.op1.expr
                if isinstance(model.op1, OpScalarMul)
                else MathNum(value=1)
            )
            expr2 = (
                model.op2.expr
                if isinstance(model.op2, OpScalarMul)
                else MathNum(value=1)
            )
            op = model.op2.op if isinstance(model.op2, OpScalarMul) else model.op2
            return OpScalarMul(op=op, expr=MathAdd(expr1=expr1, expr2=expr2))

        i = 0
        while True:
            if term1[i] > term2[i]:
                return OpAdd(
                    op1=model.op2,
                    op2=model.op1,
                )
            if term1[i] < term2[i]:
                return OpAdd(op1=model.op1, op2=model.op2)
            if term1[i] == term2[i]:
                i += 1
                continue
