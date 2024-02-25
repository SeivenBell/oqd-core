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

from quantumion.compiler.flow import *

########################################################################################

I, X, Y, Z, P, M = PauliI(), PauliX(), PauliY(), PauliZ(), PauliPlus(), PauliMinus()
A, C, J = Annihilation(), Creation(), Identity()

########################################################################################

if __name__ == "__main__":
    op = (X + X) @ (A * C)

    fg = CanonicalizationFlow2(name="g1")

    op = fg(op).model

    pprint(op.accept(PrintOperator()))

    console = Console(record=True)
    with console.capture() as capture:
        console.print(fg.traversal)
    string = console.export_text()

    with open("_console.py", mode="w", encoding="utf8") as f:
        f.write(string)
