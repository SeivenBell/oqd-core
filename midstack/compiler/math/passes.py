from midstack.compiler.walk import Post
from midstack.compiler.math.rules import EvaluateMathExpr

########################################################################################

__all__ = [
    "evaluate_math_expr",
]

########################################################################################


def evaluate_math_expr(model, output_mode="numeric"):
    """
    This pass evaluates MathExpr objects and outputs the results in numeric/string format
    """
    if output_mode == "numeric":
        return Post(EvaluateMathExpr())(model=model)
    elif output_mode == "str":
        return str(Post(EvaluateMathExpr())(model=model))
    else:
        raise TypeError("Invalid type of {}".format(output_mode))
