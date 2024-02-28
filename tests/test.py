from rich import print as pprint
from rich.console import Console

import types

########################################################################################


from quantumion.interface.math import *
from quantumion.interface.analog.operator import *

from quantumion.compiler.visitor import Visitor, Transformer
from quantumion.compiler.math import *
from quantumion.compiler.analog.base import *
from quantumion.compiler.analog.canonicalize import *
from quantumion.compiler.analog.verify import *

from quantumion.compiler.flow import *

########################################################################################

I, X, Y, Z, P, M = PauliI(), PauliX(), PauliY(), PauliZ(), PauliPlus(), PauliMinus()
A, C, J = Annihilation(), Creation(), Identity()

########################################################################################


class TestFlow(FlowGraph):
    nodes = [
        CanonicalizationFlow(name="n1"),
        FlowTerminal(name="terminal1"),
        FlowTerminal(name="terminal2"),
    ]
    rootnode = "n1"
    forward_decorators = ForwardDecorators()

    @forward_decorators.catch_error(redirect="terminal2")
    @forward_decorators.forward_fixed_point(done="terminal1")
    def forward_n1(self, model):
        pass

    pass


class TestFlow2(FlowGraph):
    nodes = [
        TestFlow(name="n1"),
        FlowTerminal(name="terminal1"),
        FlowTerminal(name="terminal2"),
    ]
    rootnode = "n1"
    forward_decorators = ForwardDecorators()

    @forward_decorators.forward_branch_from_subgraph_exit(
        branch={"terminal1": "terminal1", "terminal2": "terminal2"}
    )
    def forward_n1(self, model):
        pass

    pass


########################################################################################
if __name__ == "__main__":
    op = X + Y

    fg = TestFlow2(name="_")

    op = fg(op).model
    pprint(op.accept(PrintOperator()))

    console = Console(record=True)
    with console.capture() as capture:
        console.print(fg.traversal)
    string = console.export_text()

    with open("_console.py", mode="w", encoding="utf8") as f:
        f.write(string)
