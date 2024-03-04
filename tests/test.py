import os

from rich import print as pprint
from rich.console import Console

import types

import networkx as nx

from matplotlib import pyplot as plt

import numpy as np

from functools import reduce
from quantumion.compiler.flow import FlowOut, Traversal

########################################################################################


from quantumion.interface.math import *
from quantumion.interface.analog.operator import *

from quantumion.compiler.visitor import Visitor, Transformer
from quantumion.compiler.math import *
from quantumion.compiler.analog.base import *
from quantumion.compiler.analog.canonicalize import *
from quantumion.compiler.analog.verify import *
from quantumion.compiler.flow.visualization import *

from quantumion.compiler.flow import *

########################################################################################

I, X, Y, Z, P, M = PauliI(), PauliX(), PauliY(), PauliZ(), PauliPlus(), PauliMinus()
A, C, J = Annihilation(), Creation(), Identity()


########################################################################################


def random_mathexpr(terms):
    return MathStr(
        string="(".join(
            [
                "{}{}({}{}{})".format(
                    "-+"[np.random.randint(0, 2)],
                    "\nsin\ncos\ntan\nexp\nlog\nsinh\ncosh\ntanh".splitlines()[
                        np.random.randint(0, 9) * np.random.randint(0, 2)
                    ],
                    "-+"[np.random.randint(0, 2)],
                    [
                        str(np.random.randint(0, 26)),
                        chr(np.random.randint(0, 26) + 97),
                    ][np.random.randint(0, 2)],
                    ["", "* 1j"][np.random.randint(0, 2)],
                )
                + "+*"[np.random.randint(0, 2)]
                for _ in range(terms)
            ]
        )
        + f"{terms}"
        + ")" * (terms - 1)
    )


def random_operator(terms, pauli, ladder, math_terms):
    return reduce(
        (
            lambda a, b: [Operator.__add__, Operator.__mul__][np.random.randint(0, 2)](
                a, b
            )
        ),
        [
            reduce(
                Operator.__matmul__,
                [[I, X, Y, Z][np.random.randint(0, 4)] for _ in range(pauli)]
                + [[J, A, C][np.random.randint(0, 3)] for _ in range(ladder)],
            )
            * (random_mathexpr(math_terms))
            for _ in range(terms)
        ],
    )


########################################################################################


class TestFlowNode(FlowNode):
    def __call__(self, model, traversal=Traversal()) -> FlowOut:
        try:
            traversal.sites[-2].emission["terminate"]
        except:
            return FlowOut(model=model + 1, emission={"terminate": False})

        if not traversal.sites[-2].emission["terminate"]:
            return FlowOut(model=model, emission={"terminate": True})


class TestFlowGraph(FlowGraph):
    nodes = [
        TestFlowNode(name="n1"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "n1"

    forward_decorators = ForwardDecorators()

    @forward_decorators.catch_error(redirect="terminal")
    @forward_decorators.forward_branch_from_emission(
        key="terminate", branch={True: "terminal", False: "n1"}
    )
    def forward_n1(self, model):
        pass


class TestFlowGraph2(FlowGraph):
    nodes = [
        TestFlowGraph(name="g1"),
        FlowTerminal(name="terminal"),
    ]
    rootnode = "g1"

    forward_decorators = ForwardDecorators()

    @forward_decorators.forward_once(done="terminal")
    def forward_g1(self, model):
        pass


########################################################################################

if __name__ == "__main__":

    model = random_operator(2, 1, 1, 1)
    fg = CanonicalizationFlow(name="_")
    model = fg(model).model

    ########################################################################################

    # # console = Console(record=True)
    # # with console.capture() as capture:
    # #     console.print(fg.traversal)
    # # string = console.export_text()

    # # with open("_console.py", mode="w", encoding="utf8") as f:
    # #     f.write(string)

    ########################################################################################

    import argparse

    from flowgraph.mkdocs import graph_to_mkdocs

    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()

    fr = fg.forward_decorators.rules
    ft = fg.traversal

    graph_to_mkdocs(
        markdown_flowrules(fg),
        markdown_traversal(ft),
        markdown_flowgraph(ft),
        serve=args.serve,
    )

    pass
