from typing import Any, Union

########################################################################################

from quantumion.interface.math import MathNum, MathImag, MathAdd, MathExpr
from quantumion.interface.analog import *

from quantumion.compiler.analog.base import AnalogCircuitTransformer, AnalogCircuitVisitor

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
    "CanonicalizationVerificationOperator",
    "CanonicalFormError",
    "CanonicalizationVerificationOperatorDistribute",
    "CanonicalizationVerificationGatherMathExpr",
    "CanonicalizationVerificationProperOrder",
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

class CanonicalFormError(Exception):
    """
    Error class for canonical form (maybe we need it to put it elsewhere)
    """
    pass

class CanonicalizationVerificationOpSeq(AnalogCircuitVisitor): # check using SortedOrder
    def __init__(self):
        self._current_pauli = None
        self._map_pauli_top_idx = {
            'PauliI': 0,
            'PauliX': 1,
            'PauliY': 2,
            'PauliZ': 3
        }
    def visit_OperatorScalarMul(self, model: OperatorScalarMul): # single register
        if isinstance(model.op, (PauliX, PauliY, PauliZ, PauliI)):
            if self._current_pauli == None:
                self._current_pauli = model.op
            elif self._map_pauli_top_idx[model.op.__class__.__name__] < self._map_pauli_top_idx[self._current_pauli.__class__.__name__]:
                raise CanonicalFormError("{} is before {}".format(model.op.__class__.__name__, self._current_pauli.__class__.__name__))
    
    def visit_OperatorAdd(self, model: OperatorAdd):
        if isinstance(model.op1, OperatorAdd) and isinstance(model.op2, OperatorScalarMul):
            self.visit(model.op2)
            self.visit(model.op1)
        elif isinstance(model.op1, OperatorScalarMul) and isinstance(model.op2, OperatorScalarMul):
            self.visit(model.op1)
            self.visit(model.op2)
        else:
            raise CanonicalFormError("Incorrect canonical addition")
class CanonicalizationVerificationOperator(AnalogCircuitVisitor):
    def __init__(self):
        self.allowed_ops = Union[
            OperatorTerminal,
            OperatorMul,
            OperatorKron,
        ]
    def visit_OperatorAdd(self, model: OperatorAdd):
        if isinstance(model.op1, OperatorAdd) and isinstance(model.op2, OperatorScalarMul):
            self.visit(model.op1)
            self.visit(model.op2)
        elif isinstance(model.op1, OperatorScalarMul) and isinstance(model.op2, OperatorScalarMul):
            self.visit(model.op1)
            self.visit(model.op2)        
        else:
            raise CanonicalFormError("Incorrect canonical addition")
        
    def visit_OperatorMul(self, model: OperatorMul):
        _allowed_prod_ops = Union[Ladder,
                                  OperatorMul,
                                  ]
        """
        OpMul should not have OpKron and Anhilitation or something else. It should not have opkron at all
        """
        if isinstance(model.op1, OperatorMul): # check op2 ladder
            self.visit(model=model.op1)

        if isinstance(model.op2, OperatorMul): # check op1 ladder
            self.visit(model = model.op2)

        if not (isinstance(model.op1, _allowed_prod_ops) and isinstance(model.op2, _allowed_prod_ops)):
            raise CanonicalFormError("Incorrect canonical Operator multiplication") # pauli algebra not fully applied

        
    def visit_OperatorKron(self, model: OperatorKron):
        if isinstance(model.op1, (OperatorMul, OperatorKron)):
            self.visit(model=model.op1)
        
        if isinstance(model.op2, (OperatorMul, OperatorKron)): # ProperOrder: no need and raise error for not proper order
            self.visit(model=model.op2)
        
        if not(isinstance(model.op1, self.allowed_ops) and isinstance(model.op2, self.allowed_ops)): # terminal
            raise CanonicalFormError("Incorrect canonical kron")
        
    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, self.allowed_ops): # paulis and ladders are needed for edge cases (i.e. for single register systems)
            self.visit(model = model.op)
        else:
            raise CanonicalFormError("Incorrect canonical scalar operator multiplication")
        
    def visit_OperatorSub(self, model: OperatorSub):
        if isinstance(model, OperatorSub):
            raise CanonicalFormError("Subtraction of terms present")


class CanonicalizationVerificationOperatorDistribute(AnalogCircuitVisitor):
    def __init__(self):
        self.allowed_ops = Union[
                OperatorTerminal,
                Ladder,
                OperatorMul,
                OperatorScalarMul,
                OperatorKron,
            ]
    def _visit(self, model: Any) -> Any:
        if isinstance(model, (OperatorMul, OperatorKron)):
            self.visit_OperatorMulKronScalMul(model)
        else:
            super(self.__class__, self)._visit(model)
    
    def visit_OperatorMulKronScalMul(self, model: (OperatorMul, OperatorKron)):
        if not(isinstance(model.op1, self.allowed_ops) and isinstance(model.op2, self.allowed_ops)):
            raise CanonicalFormError("Incomplete Operator Distribution")
        else:
            self.visit(model.op1)
            self.visit(model.op2)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if not(isinstance(model.op, self.allowed_ops)):
            raise CanonicalFormError("Scalar multiplication of operators not simplified fully")
        else:
            self.visit(model = model.op)

class CanonicalizationVerificationGatherMathExpr(AnalogCircuitVisitor):
    """Assuming that OperatorDistribute has already been fully ran"""
    def _visit(self, model: Any) -> Any:
        if isinstance(model, (OperatorMul, OperatorKron)):
            self.visit_OperatorMulKron(model)
        else:
            super(self.__class__, self)._visit(model)
    
    def visit_OperatorMulKron(self, model: (OperatorMul, OperatorKron)):
        if isinstance(model.op1, OperatorScalarMul) or isinstance(model.op2, OperatorScalarMul):
            raise CanonicalFormError("Incomplete Gather Math Expression")
        else:
            self.visit(model.op1)
            self.visit(model.op2)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, OperatorScalarMul):
            raise CanonicalFormError("Incomplete scalar multiplications after GatherMathExpression")
        else:
            self.visit(model = model.op)

class CanonicalizationVerificationProperOrder(AnalogCircuitVisitor):
    """Assumptions:
        None
    """
    def _visit(self, model: Any) -> Any:
        if isinstance(model, (OperatorAdd, OperatorMul, OperatorKron)):
            self.visit_OperatorAddMulKron(model)
        else:
            super(self.__class__, self)._visit(model)

    def visit_OperatorAddMulKron(self, model: (OperatorAdd, OperatorMul, OperatorKron)):
        if isinstance(model.op2, model.__class__):
            raise CanonicalFormError("Incorrect Proper Ordering")
        else:
            self.visit(model.op1)
            self.visit(model.op2)

    def visit_OperatorScalarMul(self, model: OperatorScalarMul):
        if isinstance(model.op, model.__class__):
            raise CanonicalFormError("Incorrect Proper Ordering (for scalar multiplication)")
        else:
            self.visit(model.op)

class CanonicalizationVerificationPruneIdentity(AnalogCircuitVisitor):
    pass

class CanonicalizationVerificationPauliAlgebra(AnalogCircuitVisitor):
    pass

class CanonicalizationVerificationGatherPauli(AnalogCircuitVisitor):
    pass

class CanonicalizationVerificationNormalOrder(AnalogCircuitVisitor):
    pass

class CanonicalizationVerificationSortedOrder(AnalogCircuitVisitor):
    pass
if __name__ == '__main__':
    from rich import print as pprint
    from quantumion.compiler.analog import *
    X, Y, Z, I = PauliX(), PauliY(), PauliZ(), PauliI()
    A, C, LI =  Annihilation(), Creation(), Identity()

    test_op = X @ (A * A * C) @ (Y @ (A*C*A*A*C*LI))
    test_op = 1*(I @ A*A) + 3*(X @ A*A) + 7*(Y @ A*A) + (Z @ A*A) + 7 * (Z @ A*C)
    test_op = 1*(I @ (A*A)) + 3*(X @ (A*A))# + 7*(X @ A*A) + 6* (Z @ (A*A)) + 7 * (Z @ (A*C))
    ### test with nested addition and it seems to work
    #@test_op = 2*(I @ (A*C) @ X @ (C*A*A*A*C*LI*A) @ (X * Y)) 
    test_op = (3*(I*I)) + (2*(X*X))
    test_op = (3*(3*(3*(A*A)))) + (2*(C*C))
    test_op = 1*X + 2*I
    #test_op = 2*X*(A+Y) + 3*Y*Y
    test_op = A * A * C
    #test_op = X*(A+Y)
    #test_op = 11*2*(2*(2*X*A))
    #test_op = 2*X*(Z+Y) + 2 * Z + Z*(A*(A*(1*(6 * A*A))))
    test_op = Z*A*(A*(1*(6 * A*A)))
    #test_op = 2*(I @ (Y*X) @ X @ (C*A*A*A*C*LI*A) @ (C*X)) 
    #test_op = Z*A*A
    #test_op = X @ (Y @ (Y @ (X * Y)))
    #test_op = 3*X + (X@X) + 2*(X)
    ########################################################################
    # math expre
    # test_op = 2*(X@(7*Y*(1j+2)*Y)) + 6*(Z@(-3j*Y)) 
    # test_op = X * ((2+3)*X)
    test_op = 2j*(5*(3* (X + Y)) + 3* (Z @ A*A*C*A))
    test_op = 3* (X + Y)
    test_op = (3 * 3 * 3) * ((X * Y) @ (A*C))#(3*(3*(X*Y)))
    test_op = I+(2*(X+Y))
    test_op = Z+(X+(2*Y))
    test_op = Z+(2*(X@(2*I)+Y))
    test_op = Z*(2*I)+ ((5*Y) + 8*Z) ### showing gathermathexpr not req
    test_op = 2*(Z+I) + 3*((A+Y) + Z) ### showing distribute is req
    test_op = (A @ C) @ (2* (X + (2*Y)+Z))
    pprint(test_op.accept(VerbosePrintOperator()))
    pprint(test_op)
    #pprint(test_op.accept(GatherMathExpr()).accept(GatherMathExpr()).accept(GatherMathExpr()).accept(GatherMathExpr()).accept(GatherMathExpr()))#.accept(PrintOperator()))
    pprint(test_op.accept(CanonicalizationVerificationProperOrder()))
    ########################################################################
    ### assumptions are needed -> without some assumptions of tree structure this is impossible.

    # PauliAlgebra 
