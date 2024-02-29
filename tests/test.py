import os

from rich import print as pprint
from rich.console import Console

import types

import networkx as nx

from matplotlib import pyplot as plt

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
        CanonicalizationFlow(name="canonicalization"),
        FlowTerminal(name="terminal"),
        FlowTerminal(name="error"),
    ]
    rootnode = "canonicalization"
    forward_decorators = ForwardDecorators()

    @forward_decorators.catch_error(redirect="error")
    @forward_decorators.forward_once(done="terminal")
    def forward_canonicalization(self, model):
        pass

    pass


########################################################################################

if __name__ == "__main__":
    op = X * (Y + Z) @ (A * C)

    fg = TestFlow(name="cf")

    op = fg(op).model
    pprint(op.accept(PrintOperator()))

    # console = Console(record=True)
    # with console.capture() as capture:
    #     console.print(fg.traversal)
    # string = console.export_text()

    # with open("_console.py", mode="w", encoding="utf8") as f:
    #     f.write(string)

    fr = fg.forward_decorators.rules
    ft = fg.traversal

    ########################################################################################

    import argparse

    from flowgraph.mkdocs import graph_to_mkdocs

    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()

    def mermaid_rules(flowgraph, tabname="Full"):
        mermaid_string = '=== "{}"\n\t'.format(tabname.title())
        mermaid_string += "\n\t".join(
            flowgraph.forward_decorators.rules.accept(MermaidFlowGraph()).splitlines()
        )
        for node in flowgraph.nodes:
            if isinstance(node, FlowGraph):
                mermaid_string += "\n\t".join(
                    ("\n" + mermaid_rules(node, node.name) + "\n").splitlines()
                )
        return mermaid_string

    def mermaid_traversal(traversal, tabname="Full"):
        mermaid_string = '=== "{}"\n\t'.format(tabname.title())
        mermaid_string += "\n\t".join(traversal.accept(MermaidFlowGraph()).splitlines())
        for site in traversal.sites:
            if site.subtraversal:
                mermaid_string += "\n\t".join(
                    (
                        "\n"
                        + mermaid_traversal(
                            site.subtraversal,
                            tabname=f"{site.node} (Site {site.site})",
                        )
                        + "\n"
                    ).splitlines()
                )
        return mermaid_string

    graph_to_mkdocs(mermaid_rules(fg), mermaid_traversal(ft), serve=args.serve)
