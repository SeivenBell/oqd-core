from quantumion.compilerv2.rewriter import Chain, FixedPoint
from quantumion.compilerv2.walk import Post, Pre
from quantumion.compilerv2.analog.rewrite.canonicalize import *
from quantumion.compilerv2.analog.verify.canonicalization import *
from quantumion.compilerv2.math.rules import (
    DistributeMathExpr,
    ProperOrderMathExpr,
    PartitionMathExpr,
)

########################################################################################

__all__ = [
    "dist_chain",
    "pauli_chain",
    "normal_order_chain",
    "scale_terms_chain",
    "math_chain",
    "verify_canonicalization",
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
    return Chain(
        FixedPoint(dist_chain),
        FixedPoint(Post(ProperOrder())),
        FixedPoint(pauli_chain),
        FixedPoint(Post(GatherPauli())),
        FixedPoint(normal_order_chain),
        FixedPoint(Post(PruneIdentity())),
        FixedPoint(scale_terms_chain),
        FixedPoint(Post(SortedOrder())),
        math_chain,
        verify_canonicalization,  # running verifier
    )(model=model)
