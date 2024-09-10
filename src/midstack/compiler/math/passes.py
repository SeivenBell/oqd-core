from midstack.compiler.walk import Post
from midstack.compiler.rewriter import Chain
from midstack.compiler.math.rules import (
    EvaluateMathExpr,
    SimplifyMathExpr,
    PrintMathExpr,
)

########################################################################################

__all__ = [
    "evaluate_math_expr",
    "simplify_math_expr",
]

########################################################################################


evaluate_math_expr = Post(EvaluateMathExpr())


simplify_math_expr = Chain(
    Post(SimplifyMathExpr()),
    Post(PrintMathExpr()),
)
