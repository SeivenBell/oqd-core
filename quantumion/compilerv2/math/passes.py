from quantumion.compilerv2.walk import Post
from quantumion.compilerv2.math.utils import EvaluateMathExpr

########################################################################################

__all__ = [
    "evaluate_math_expr",
]

########################################################################################


def evaluate_math_expr(model, output_mode="numeric"):
    if output_mode == "numeric":
        return Post(EvaluateMathExpr())(model=model)
    elif output_mode == "str":
        return str(Post(EvaluateMathExpr())(model=model))
    else:
        raise TypeError("Invalid type of {}".format(output_mode))
