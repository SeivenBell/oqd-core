import os

from rich import print as pprint
from rich.console import Console

import types

import networkx as nx

from matplotlib import pyplot as plt

import numpy as np

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


def random_hexcolor():
    r = lambda: np.random.randint(0, 255)
    return "#%02X%02X%02X" % (r(), r(), r())


class MermaidMathExpr(Transformer):

    def emit(self, model):
        self.element = 0

        self.mermaid_string = "```mermaid\ngraph TD\n"
        model.accept(self)
        self.mermaid_string += "".join(
            [
                f"classDef {model} stroke:{random_hexcolor()}\n"
                for model in [
                    "MathAdd",
                    "MathSub",
                    "MathMul",
                    "MathDiv",
                    "MathFunc",
                    "MathNum",
                    "MathVar",
                    "MathImag",
                ]
            ]
        )
        self.mermaid_string += "```\n"

        return self.mermaid_string

    def visit_MathImag(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            model.__class__.__name__,
        )
        self.element += 1

        return f"element{element}"

    def visit_MathVar(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}<br/>{}<br/>{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            "-" * len(model.__class__.__name__),
            "name = #quot;{}#quot;".format(model.name),
            model.__class__.__name__,
        )
        self.element += 1

        return f"element{element}"

    def visit_MathNum(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}<br/>{}<br/>{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            "-" * len(model.__class__.__name__),
            "value = {}".format(model.value),
            model.__class__.__name__,
        )
        self.element += 1

        return f"element{element}"

    def visit_MathBinaryOp(self, model):
        left = self.visit(model.expr1)
        right = self.visit(model.expr2)

        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            model.__class__.__name__,
        )

        self.mermaid_string += f"element{element} --> {left} & {right}\n"

        self.element += 1

        return f"element{element}"

    def visit_MathFunc(self, model):
        expr = self.visit(model.expr)

        element = self.element
        self.mermaid_string += 'element{}("{}<br/>{}<br/>{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            "-" * len(model.__class__.__name__),
            "func = {}".format(model.func),
            model.__class__.__name__,
        )

        self.mermaid_string += f"element{element} --> {expr}\n"

        self.element += 1

        return f"element{element}"


class MermaidOperator(Transformer):

    def emit(self, model):
        self.element = 0

        self.mermaid_string = "```mermaid\ngraph TD\n"
        model.accept(self)
        self.mermaid_string += "".join(
            [
                f"classDef {model} stroke:{random_hexcolor()}\n"
                for model in [
                    "Pauli",
                    "Ladder",
                    "OperatorAdd",
                    "OperatorScalarMul",
                    "OperatorKron",
                    "OperatorMul",
                ]
            ]
        )
        self.mermaid_string += "```\n"

        return self.mermaid_string

    def visit_MathExpr(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}<br/>{}<br/>{}"):::{}\n'.format(
            self.element,
            "MathExpr",
            "-" * len("MathExpr"),
            "expr = #quot;{}#quot;".format(model.accept(PrintMathExpr())),
            "MathExpr",
        )
        self.element += 1

        return f"element{element}"

    def visit_Pauli(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element, model.__class__.__name__, "Pauli"
        )
        self.element += 1

        return f"element{element}"

    def visit_Ladder(self, model):
        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element, model.__class__.__name__, "Ladder"
        )
        self.element += 1

        return f"element{element}"

    def visit_OperatorBinaryOp(self, model):
        left = self.visit(model.op1)
        right = self.visit(model.op2)

        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            model.__class__.__name__,
        )

        self.mermaid_string += f"element{element} --> {left} & {right}\n"

        self.element += 1

        return f"element{element}"

    def visit_OperatorScalarMul(self, model):
        expr = self.visit(model.expr)
        op = self.visit(model.op)

        element = self.element
        self.mermaid_string += 'element{}("{}"):::{}\n'.format(
            self.element,
            model.__class__.__name__,
            model.__class__.__name__,
        )

        self.mermaid_string += f"element{element} --> {expr} & {op}\n"

        self.element += 1

        return f"element{element}"


########################################################################################


class MathCanonicalizationFlow(FlowGraph):
    nodes = [
        FlowTerminal(name="terminal"),
        TransformerFlowNode(visitor=DistributeMathExpr(), name="dist"),
        TransformerFlowNode(visitor=ProperOrderMathExpr(), name="proper"),
        TransformerFlowNode(visitor=PartitionMathExpr(), name="part"),
    ]
    rootnode = "dist"
    forward_decorators = ForwardDecorators()

    @forward_decorators.forward_fixed_point(done="proper")
    def forward_dist(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="part")
    def forward_proper(self, model):
        pass

    @forward_decorators.forward_fixed_point(done="terminal")
    def forward_part(self, model):
        pass

    pass


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
                    " j"[np.random.randint(0, 2)],
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

if __name__ == "__main__":
    # k = np.random.randint(1, 6)
    # expr = random_mathexpr(k)
    # pprint(expr.accept(PrintMathExpr()))

    # fg = MathCanonicalizationFlow(name="_")

    # expr = fg(expr).model
    # pprint(expr.accept(PrintMathExpr()))

    # mermaid_string = MermaidMathExpr().emit(expr)

    # with open("test.md", mode="w") as f:
    #     f.write(mermaid_string)

    ########################################################################################

    from functools import reduce

    k = np.random.randint(1, 5)
    l = np.random.randint(1, 3)
    m = np.random.randint(1, 2)
    n = np.random.randint(1, 2)
    op = random_operator(k, l, m, n)
    # op = (
    #     (MathStr(string="(k + 1)") * (PauliI() @ Creation()))
    #     * (MathStr(string="(o + 1)") * (PauliX() @ Identity()))
    #     + MathStr(string="(-1 * 19 + 1)") * (PauliX() @ Creation())
    # ) * (MathStr(string="(cosh(-1 * (0.0 + 1j * 1.0)) + 1)") * (PauliY() @ Identity()))

    fg = CanonicalizationFlow(name="_")

    pprint(op.accept(PrintOperator()))

    op = fg(op).model
    pprint(op.accept(PrintOperator()))

    mermaid_string = MermaidOperator().emit(op)

    with open("test.md", mode="w") as f:
        f.write(mermaid_string)

    ########################################################################################

    # op = X @ (A * C)

    # fg = TestFlow(name="cf")

    # op = fg(op).model
    # pprint(op.accept(PrintOperator()))

    # # console = Console(record=True)
    # # with console.capture() as capture:
    # #     console.print(fg.traversal)
    # # string = console.export_text()

    # # with open("_console.py", mode="w", encoding="utf8") as f:
    # #     f.write(string)

    ########################################################################################

    # import argparse

    # from flowgraph.mkdocs import graph_to_mkdocs

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--serve", action="store_true")
    # args = parser.parse_args()

    # def mermaid_rules(flowgraph, tabname="Main"):
    #     mermaid_string = '=== "{}"\n\t'.format(tabname.title())
    #     mermaid_string += "\n\t".join(
    #         flowgraph.forward_decorators.rules.accept(MermaidFlowGraph()).splitlines()
    #     )
    #     for node in flowgraph.nodes:
    #         if isinstance(node, FlowGraph):
    #             mermaid_string += "\n\t".join(
    #                 ("\n" + mermaid_rules(node, node.name) + "\n").splitlines()
    #             )
    #     return mermaid_string

    # def mermaid_traversal(traversal, tabname="Main"):
    #     mermaid_string = '=== "{}"\n\t'.format(tabname.title())
    #     mermaid_string += "\n\t".join(traversal.accept(MermaidFlowGraph()).splitlines())
    #     for site in traversal.sites:
    #         if site.subtraversal:
    #             mermaid_string += "\n\t".join(
    #                 (
    #                     "\n"
    #                     + mermaid_traversal(
    #                         site.subtraversal,
    #                         tabname=f"{site.node} (Site {site.site})",
    #                     )
    #                     + "\n"
    #                 ).splitlines()
    #             )
    #     return mermaid_string

    # fr = fg.forward_decorators.rules
    # ft = fg.traversal

    # graph_to_mkdocs(mermaid_rules(fg), mermaid_traversal(ft), serve=args.serve)
