from quantumion.compilerv2.rewriter import *
from quantumion.compilerv2.walk import *
from quantumion.compilerv2.canonicalization.rules import *
from quantumion.compilerv2.canonicalization.verification import *
from quantumion.compilerv2.math.rules import *

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

math_chain = Chain(
    FixedPoint(Post(DistributeMathExpr())),
    FixedPoint(Post(ProperOrderMathExpr())),
    FixedPoint(Post(PartitionMathExpr())),
)

canonicalize = Chain(FixedPoint(dist_chain), 
            FixedPoint(Post(ProperOrder())), 
            FixedPoint(pauli_chain), 
            FixedPoint(Post(GatherPauli())),
            FixedPoint(normal_order_chain),
            FixedPoint(Post(PruneIdentity())),
            FixedPoint(scale_terms_chain),
            FixedPoint(Post(SortedOrder())),
            math_chain
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
    # op = X@(X+(3*(Y)))
    op = 2*X + (3*Y) *((2*I) + (1*X))

    output = compiler(op)

    verifier(output)

    pprint(output.accept(VerbosePrintOperator()))
    """
    partition does :
    (((2) * PauliX()) + ((3 * 2) * PauliY())) + ((((3 * 1) * -1) * 1j) * PauliZ())
    to
    (((2) * PauliX()) + ((3 * 2) * PauliY())) + ((((1j * 3) * 1) * -1) * PauliZ())  
    """