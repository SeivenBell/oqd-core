from rich import print as pprint
from rich.console import Console

import types

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


class TestVisitor(Visitor):
    def visit_Operator(self, model):
        raise TypeError
        pass

    def visit_OperatorAdd(self, model):
        raise AssertionError
        pass


########################################################################################


class TestFlow(FlowGraph):
    nodes = [
        VisitorFlowNode(visitor=TestVisitor(), name="n1"),
        FlowTerminal(name="terminal1"),
        FlowTerminal(name="terminal2"),
        FlowTerminal(name="terminal3"),
    ]
    rootnode = "n1"
    forward_decorators = ForwardDecorators()

    @forward_decorators.catch_errors_and_branch(
        branch={AssertionError: "terminal2", TypeError: "terminal3"}
    )
    @forward_decorators.forward_once(done="terminal1")
    def forward_n1(self, model):
        pass


########################################################################################

# forward_decorators = ForwardDecorators()


# @forward_decorators.catch_error(redirect="terminal2")
# @forward_decorators.forward_once(done="terminal1")
# def forward_g1(self, model):
#     pass


# TestFlow2 = type(
#     "TestFlow2",
#     (FlowGraph,),
#     dict(
#         nodes=[
#             CanonicalizationFlow(name="g1"),
#             FlowTerminal(name="terminal1"),
#             FlowTerminal(name="terminal2"),
#         ],
#         rootnode="g1",
#         forward_decorators=forward_decorators,
#         forward_g1=forward_g1,
#     ),
# )

########################################################################################
if __name__ == "__main__":
    op = X + Y

    fg = TestFlow(name="g1")

    op = fg(op).model

    pprint(op.accept(PrintOperator()))

    console = Console(record=True)
    with console.capture() as capture:
        console.print(fg.traversal)
    string = console.export_text()

    with open("_console.py", mode="w", encoding="utf8") as f:
        f.write(string)

    pprint(fg.traversal)
    pprint(fg.forward_decorators.rules)
