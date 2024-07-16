from quantumion.compilerv2.rewriter import *
from quantumion.compilerv2.walk import *
from quantumion.compilerv2.canonicalization.rules import *
from quantumion.compilerv2.canonicalization.verification import *

dist_chain = Chain(
    FixedPoint(Post(OperatorDistribute())), 
    FixedPoint(Post(GatherMathExpr())), 
    FixedPoint(Post(OperatorDistribute())),
    )

pauli_chain = Chain(
    FixedPoint(Post(PauliAlgebra())),
    FixedPoint(Post(GatherMathExpr())),
    FixedPoint(Post(PauliAlgebra()))
)

normal_order_chain = Chain(
    FixedPoint(Post(NormalOrder())),
    FixedPoint(Post(OperatorDistribute())),
    FixedPoint(Post(GatherMathExpr())),
    FixedPoint(Post(ProperOrder())),
    FixedPoint(Post(NormalOrder())),
)

scale_terms_chain = Chain(
    FixedPoint(Pre(ScaleTerms())),
    FixedPoint(Post(GatherMathExpr()))
)

compiler = Chain(FixedPoint(dist_chain), 
            FixedPoint(Post(ProperOrder())), 
            FixedPoint(pauli_chain), 
            FixedPoint(Post(GatherPauli())),
            FixedPoint(normal_order_chain),
            FixedPoint(Post(PruneIdentity())),
            FixedPoint(scale_terms_chain),
            FixedPoint(Post(SortedOrder()))
            )

verifier = Chain(
    Post(CanVerOperatorDistribute()),
    Post(CanVerGatherMathExpr()),
    Post(CanVerProperOrder()),
    Post(CanVerPauliAlgebra()),
    Post(CanVerGatherPauli()),
    Post(CanVerNormalOrder()),
    Post(CanVerPruneIdentity()),
    Post(CanVerSortedOrder()),
    Pre(CanVerScaleTerm())
)

if __name__ == '__main__':
    from quantumion.compiler.analog.base import *
    X, Y, Z, I, A, C, LI = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()

    op =  A@(Z*I) + A@I # gatherpauli does not give error (previously used to.) Now PauliAlgebra does give error

    output = compiler(op)
    output =  2*(X@Z)

    verifier(output)

    pprint(output.accept(PrintOperator()))