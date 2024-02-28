from typing import Any, Union

########################################################################################

from quantumion.interface.math import MathNum, MathImag, MathAdd
from quantumion.interface.analog import *

from quantumion.compiler.analog.base import AnalogCircuitTransformer

########################################################################################

__all__ = [
    "PruneIdentity",
    "PauliAlgebra",
    "GatherMathExpr",
    "GatherPauli",
    "OperatorDistribute",
    "ProperOrder",
    "NormalOrder",
    "TermIndex",
    "SortedOrder",
]

########################################################################################


class PruneIdentity(AnalogCircuitTransformer):
    def visit_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, (Identity, PauliI)):
            return self.visit(model.op2)
        if isinstance(model.op2, (Identity, PauliI)):
            return self.visit(model.op1)
        return OperatorMul(op1=self.visit(model.op1), op2=self.visit(model.op2))


class PauliAlgebra(AnalogCircuitTransformer):
    def visit_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, Pauli) and isinstance(model.op2, Pauli):
            if isinstance(model.op1, PauliI):
                return self.visit(model.op2)
            if isinstance(model.op2, PauliI):
                return self.visit(model.op1)
            if model.op1 == model.op2:
                return PauliI()
            if isinstance(model.op1, PauliX) and isinstance(model.op2, PauliY):
                return OperatorScalarMul(op=PauliZ(), expr=MathImag())
            if isinstance(model.op1, PauliY) and isinstance(model.op2, PauliZ):
                return OperatorScalarMul(op=PauliX(), expr=MathImag())
            if isinstance(model.op1, PauliZ) and isinstance(model.op2, PauliX):
                return OperatorScalarMul(op=PauliY(), expr=MathImag())
            return OperatorScalarMul(
                op=self.visit(OperatorMul(op1=model.op2, op2=model.op1)),
                expr=MathNum(value=-1),
            )
        return OperatorMul(op1=self.visit(model.op1), op2=self.visit(model.op2))


########################################################################################


class GatherMathExpr(AnalogCircuitTransformer):
    def _visit(self, model: Any) -> Any:
        if isinstance(model, (OperatorMul, OperatorKron)):
            return self.visit_OperatorMulKron(model)
        if isinstance(model, (OperatorAdd, OperatorSub)):
            return self.visit_OperatorAddSub(model)
        if isinstance(model, Operator):
            return model
        raise TypeError

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, OperatorScalarMul):
            return model.expr * model.op.expr * self.visit(model.op.op)
        return model.expr * self.visit(model.op)

    def visit_OperatorMulKron(self, model: Union[OperatorMul, OperatorKron]):
        if isinstance(model.op1, OperatorScalarMul) and isinstance(
            model.op2, OperatorScalarMul
        ):
            return (
                model.op1.expr
                * model.op2.expr
                * self.visit(model.__class__(op1=model.op1.op, op2=model.op2.op))
            )
        if isinstance(model.op1, OperatorScalarMul):
            return model.op1.expr * self.visit(
                model.__class__(op1=model.op1.op, op2=model.op2)
            )
        if isinstance(model.op2, OperatorScalarMul):
            return model.op2.expr * self.visit(
                model.__class__(op1=model.op1, op2=model.op2.op)
            )
        return model.__class__(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def visit_OperatorAddSub(self, model: Union[OperatorAdd, OperatorSub]):
        return model.__class__(op1=self.visit(model.op1), op2=self.visit(model.op2))


class GatherPauli(AnalogCircuitTransformer):
    def visit_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op2, Pauli):
            if isinstance(model.op1, Ladder):
                return OperatorKron(
                    op1=model.op2,
                    op2=model.op1,
                )
            if isinstance(model.op1, OperatorMul) and isinstance(model.op1.op2, Ladder):
                return OperatorKron(
                    op1=model.op2,
                    op2=model.op1,
                )
            if isinstance(model.op1, OperatorKron) and isinstance(
                model.op1.op2, Union[Ladder, OperatorMul]
            ):
                return OperatorKron(
                    op1=OperatorKron(op1=model.op1.op1, op2=model.op2),
                    op2=model.op1.op2,
                )
        return OperatorKron(op1=self.visit(model.op1), op2=self.visit(model.op2))


########################################################################################


class OperatorDistribute(AnalogCircuitTransformer):
    def visit_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op1, (OperatorAdd, OperatorSub)):
            return model.op1.__class__(
                op1=self.visit(OperatorMul(op1=model.op1.op1, op2=model.op2)),
                op2=self.visit(OperatorMul(op1=model.op1.op2, op2=model.op2)),
            )
        if isinstance(model.op2, (OperatorAdd, OperatorSub)):
            return model.op2.__class__(
                op1=self.visit(OperatorMul(op1=model.op1, op2=model.op2.op1)),
                op2=self.visit(OperatorMul(op1=model.op1, op2=model.op2.op2)),
            )
        if isinstance(model.op1, (OperatorKron)) and isinstance(
            model.op2, (OperatorKron)
        ):
            return OperatorKron(
                op1=OperatorMul(op1=model.op1.op1, op2=model.op2.op1),
                op2=OperatorMul(op1=model.op1.op2, op2=model.op2.op2),
            )
        return OperatorMul(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def visit_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op1, (OperatorAdd, OperatorSub)):
            return model.op1.__class__(
                op1=self.visit(OperatorKron(op1=model.op1.op1, op2=model.op2)),
                op2=self.visit(OperatorKron(op1=model.op1.op2, op2=model.op2)),
            )
        if isinstance(model.op2, (OperatorAdd, OperatorSub)):
            return model.op2.__class__(
                op1=self.visit(OperatorKron(op1=model.op1, op2=model.op2.op1)),
                op2=self.visit(OperatorKron(op1=model.op1, op2=model.op2.op2)),
            )
        return OperatorKron(op1=self.visit(model.op1), op2=self.visit(model.op2))

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, (OperatorAdd, OperatorSub)):
            return model.op.__class__(
                op1=OperatorScalarMul(op=self.visit(model.op.op1), expr=model.expr),
                op2=OperatorScalarMul(op=self.visit(model.op.op2), expr=model.expr),
            )
        return OperatorScalarMul(op=self.visit(model.op), expr=model.expr)

    def visit_OperatorSub(self, model: OperatorSub):
        return OperatorAdd(
            op1=self.visit(model.op1),
            op2=OperatorScalarMul(op=self.visit(model.op2), expr=MathNum(value=-1)),
        )


########################################################################################


class ProperOrder(AnalogCircuitTransformer):
    def _visit(self, model: Any):
        if isinstance(model, (OperatorAdd, OperatorMul, OperatorKron)):
            return self.visit_OperatorAddMulKron(model)
        return super(self.__class__, self)._visit(model)

    def visit_OperatorAddMulKron(
        self, model: Union[OperatorAdd, OperatorMul, OperatorKron]
    ):
        if isinstance(model.op2, model.__class__):
            return model.__class__(
                op1=model.__class__(
                    op1=self.visit(model.op1), op2=self.visit(model.op2.op1)
                ),
                op2=self.visit(model.op2.op2),
            )
        return model.__class__(op1=self.visit(model.op1), op2=self.visit(model.op2))


########################################################################################


class NormalOrder(AnalogCircuitTransformer):
    def visit_OperatorMul(self, model: OperatorMul):
        if isinstance(model.op2, Creation):
            if isinstance(model.op1, Annihilation):
                return OperatorSub(
                    op1=OperatorMul(op1=model.op2, op2=model.op1), op2=Identity()
                )
            if isinstance(model.op1, OperatorMul) and isinstance(
                model.op1.op2, Annihilation
            ):
                return OperatorMul(
                    op1=self.visit(model.op1.op1),
                    op2=OperatorSub(
                        op1=OperatorMul(op1=model.op2, op2=model.op1.op2),
                        op2=Identity(),
                    ),
                )
            if isinstance(model.op1, Identity):
                return OperatorMul(op1=model.op2, op2=model.op1)
            if isinstance(model.op1, OperatorMul) and isinstance(
                model.op1.op2, Identity
            ):
                return OperatorMul(
                    op1=self.visit(model.op1.op1),
                    op2=OperatorMul(op1=model.op2, op2=model.op1.op2),
                )
        return OperatorMul(op1=self.visit(model.op1), op2=self.visit(model.op2))


########################################################################################


class TermIndex(AnalogCircuitTransformer):
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

    def visit_OperatorAdd(self, model: OperatorAdd):
        term1 = (
            self.visit(model.op1)
            if isinstance(model.op1, OperatorAdd)
            else [self.visit(model.op1)]
        )
        term2 = self.visit(model.op2)
        return term1 + [term2]

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        term = self.visit(model.op)
        return term

    def visit_OperatorMul(self, model: OperatorMul):
        term1 = self.visit(model.op1)
        term2 = self.visit(model.op2)
        return [term1[0] + term2[0], term1[1] + term2[1]]

    def visit_OperatorKron(self, model: OperatorKron):
        term1 = self.visit(model.op1)
        term2 = self.visit(model.op2)
        return term1 + term2


class SortedOrder(AnalogCircuitTransformer):
    def visit_OperatorAdd(self, model: OperatorAdd):
        if isinstance(model.op1, OperatorAdd):
            term1 = TermIndex().visit(model.op1.op2)
            term2 = TermIndex().visit(model.op2)

            if term1 == term2:
                expr1 = (
                    model.op1.op2.expr
                    if isinstance(model.op1.op2, OperatorScalarMul)
                    else MathNum(value=1)
                )
                expr2 = (
                    model.op2.expr
                    if isinstance(model.op2, OperatorScalarMul)
                    else MathNum(value=1)
                )
                op = (
                    model.op2.op
                    if isinstance(model.op2, OperatorScalarMul)
                    else model.op2
                )
                return OperatorAdd(
                    op1=self.visit(model.op1.op1),
                    op2=OperatorScalarMul(
                        op=op, expr=MathAdd(expr1=expr1, expr2=expr2)
                    ),
                )

            i = 0
            while True:
                if term1[i] > term2[i]:
                    return OperatorAdd(
                        op1=self.visit(OperatorAdd(op1=model.op1.op1, op2=model.op2)),
                        op2=model.op1.op2,
                    )
                if term1[i] < term2[i]:
                    return OperatorAdd(op1=self.visit(model.op1), op2=model.op2)
                if term1[i] == term2[i]:
                    i += 1
                    continue

        term1 = TermIndex().visit(model.op1)
        term2 = TermIndex().visit(model.op2)

        if term1 == term2:
            expr1 = (
                model.op1.expr
                if isinstance(model.op1, OperatorScalarMul)
                else MathNum(value=1)
            )
            expr2 = (
                model.op2.expr
                if isinstance(model.op2, OperatorScalarMul)
                else MathNum(value=1)
            )
            op = model.op2.op if isinstance(model.op2, OperatorScalarMul) else model.op2
            return OperatorScalarMul(op=op, expr=MathAdd(expr1=expr1, expr2=expr2))

        i = 0
        while True:
            if term1[i] > term2[i]:
                return OperatorAdd(
                    op1=model.op2,
                    op2=model.op1,
                )
            if term1[i] < term2[i]:
                return OperatorAdd(op1=model.op1, op2=model.op2)
            if term1[i] == term2[i]:
                i += 1
                continue
