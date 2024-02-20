from typing import Union, List

import re

from rich import print as pprint
from rich.console import Console

########################################################################################

from quantumion.interface.math import *
from quantumion.interface.analog.operator import *

from quantumion.compiler.math import *
from quantumion.compiler.analog.base import *
from quantumion.compiler.analog.canonicalize import *
from quantumion.compiler.analog.verify import *

########################################################################################

I, X, Y, Z, P, M = PauliI(), PauliX(), PauliY(), PauliZ(), PauliPlus(), PauliMinus()
A, C, J = Annihilation(), Creation(), Identity()

########################################################################################


def repeat(model: Union[MathExpr, Operator], visitor: List[Visitor], verbose=True):
    i = 0
    while True:
        _model = model.accept(visitor())
        try:
            model.accept(VerifyHilbertSpace())
        except:
            raise Exception("{}".format(visitor.__name__))
        if _model == model:
            break
        i += 1
        model = _model

        if verbose:
            pprint(
                "\n{:^20}:".format(visitor.__name__ + str(i)),
                "\n" + model.accept(VerbosePrintOperator()),
            )

    print("Ran {} {} times".format(visitor.__name__, i))
    return model


def multivisitor(
    model: Union[MathExpr, Operator], visitors: List[Visitor], verbose=True
):
    for visitor in visitors:
        model = repeat(model, visitor, verbose)
    return model


########################################################################################

if __name__ == "__main__":
    op = (X @ C @ X @ (A * C * C * A * C * C) @ X @ X) @ A @ C

    pprint(
        "\nHilbert Space  :\n\tPauli  : {}\n\tLadder : {}\n".format(
            *op.accept(VerifyHilbertSpace())
        )
    )

    pprint(op.accept(PrintOperator()))

    print("=" * 40)
    while True:
        _op = multivisitor(
            op,
            [
                Distribute,
                GatherMathExpr,
                ProperOrder,
                GatherPauli,
                NormalOrder,
                Distribute,
                GatherMathExpr,
                ProperOrder,
                PruneIdentity,
            ],
            verbose=False,
        )
        print("=" * 40)
        if op == _op:
            break
        op = _op

    pprint(op.accept(PrintOperator()))

    pprint(
        "\nHilbert Space  :\n\tPauli  : {}\n\tLadder : {}\n".format(
            *op.accept(VerifyHilbertSpace())
        )
    )

    console = Console(record=True)
    with console.capture() as capture:
        console.print(op)
    op_str = console.export_text()

    with open("_op.py", mode="w", encoding="utf8") as f:
        f.write(op_str)
