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


def dummy_node(label):
    def call(self, model):
        if not hasattr(self, "used"):
            self.used = False

        if self.used:
            raise Exception("Node Used")

        self.used = True

        return FlowOut(model=model, emission=dict(used=self.used))

    dummy_flow_node = type(
        "DummyFlowNode{}".format(label),
        (FlowNode,),
        {
            "__call__": call,
        },
    )

    return dummy_flow_node


DummyFlowNode = dummy_node(label=1)

########################################################################################


class TestVisitor(Visitor):
    def visit_OperatorMul(self, model):
        raise TypeError
        pass

    def visit_OperatorAdd(self, model):
        raise AssertionError
        pass


########################################################################################


class TestFlow(FlowGraph):
    nodes = [
        VisitorFlowNode(visitor=TestVisitor(), name="n1"),
        DummyFlowNode(name="n2"),
        DummyFlowNode(name="n3"),
        DummyFlowNode(name="n4"),
        FlowTerminal(name="terminal1"),
        FlowTerminal(name="terminal2"),
        FlowTerminal(name="terminal3"),
        FlowTerminal(name="terminal4"),
    ]
    rootnode = "n1"
    forward_decorators = ForwardDecorators()

    @forward_decorators.catch_errors_and_branch(
        branch={AssertionError: "n2", TypeError: "n3"}
    )
    @forward_decorators.forward_once(done="terminal1")
    def forward_n1(self, model):
        pass

    @forward_decorators.catch_error(redirect="terminal2")
    @forward_decorators.forward_once(done="n4")
    def forward_n2(self, model):
        pass

    @forward_decorators.catch_error(redirect="terminal3")
    @forward_decorators.forward_once(done="n4")
    def forward_n3(self, model):
        pass

    @forward_decorators.catch_error(redirect="terminal4")
    @forward_decorators.forward_return()
    def forward_n4(self, model):
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
    op = X * Z

    fg = TestFlow(name="g1", max_steps=10)

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
