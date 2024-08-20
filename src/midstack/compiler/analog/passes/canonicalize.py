from midstack.compiler.rewriter import Chain, FixedPoint
from midstack.compiler.walk import Post, Pre, In
from midstack.compiler.analog.rewrite.canonicalize import *
from midstack.compiler.analog.verify.canonicalization import *
from midstack.compiler.analog.verify.operator import VerifyHilberSpaceDim
from midstack.compiler.math.rules import (
    DistributeMathExpr,
    ProperOrderMathExpr,
    PartitionMathExpr,
)

########################################################################################

__all__ = [
    "analog_operator_canonicalization",
]

########################################################################################

dist_chain = Chain(
    FixedPoint(Post(OperatorDistribute())),
    FixedPoint(Post(GatherMathExpr())),
    FixedPoint(Post(OperatorDistribute())),
)

pauli_chain = Chain(
    FixedPoint(Post(PauliAlgebra())),
    FixedPoint(Post(GatherMathExpr())),
    FixedPoint(Post(PauliAlgebra())),
)

normal_order_chain = Chain(
    FixedPoint(Post(NormalOrder())),
    FixedPoint(Post(OperatorDistribute())),
    FixedPoint(Post(GatherMathExpr())),
    FixedPoint(Post(ProperOrder())),
    FixedPoint(Post(NormalOrder())),
)

scale_terms_chain = Chain(
    FixedPoint(Pre(ScaleTerms())), FixedPoint(Post(GatherMathExpr()))
)

math_chain = Chain(
    FixedPoint(Post(DistributeMathExpr())),
    FixedPoint(Post(ProperOrderMathExpr())),
    FixedPoint(Post(PartitionMathExpr())),
)

verify_canonicalization = Chain(
    Post(CanVerOperatorDistribute()),
    Post(CanVerGatherMathExpr()),
    Post(CanVerProperOrder()),
    Post(CanVerPauliAlgebra()),
    Post(CanVerGatherPauli()),
    Post(CanVerNormalOrder()),
    Post(CanVerPruneIdentity()),
    Post(CanVerSortedOrder()),
    Pre(CanVerScaleTerm()),
)


def analog_operator_canonicalization(model):
    """
    This pass runs canonicalization chain for Operators with a verifies for canonicalization.

    Args:
        model (VisitableBaseModel):
               The rule only modifies [`Operator`][midstack.interface.analog.operator.Operator] in Analog level

    Returns:
        model (VisitableBaseModel):  [`Operator`][midstack.interface.analog.operator.Operator] of Analog level are in canonical form

    Assumtions:
        None

    Example:
        - for model = X@(Y + Z), output is 1*(X@Y) + 1 * (X@Z)
        - for model = [`AnalogGate`][midstack.interface.analog.operations.AnalogGate](hamiltonian = (A * J)@X), output is
            [`AnalogGate`][midstack.interface.analog.operations.AnalogGate](hamiltonian = 1 * (X@A))
            (where A = Annhiliation(), J = Identity() [Ladder])
    """
    return Chain(
        FixedPoint(dist_chain),
        FixedPoint(Post(ProperOrder())),
        FixedPoint(pauli_chain),
        FixedPoint(Post(GatherPauli())),
        In(VerifyHilberSpaceDim(), reverse=True),
        FixedPoint(normal_order_chain),
        FixedPoint(Post(PruneIdentity())),
        FixedPoint(scale_terms_chain),
        FixedPoint(Post(SortedOrder())),
        math_chain,
        verify_canonicalization,
    )(model=model)
