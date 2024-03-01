import networkx as nx

########################################################################################

from quantumion.interface.math import MathExpr
from quantumion.interface.analog.operator import Operator

from quantumion.compiler.visitor import Transformer
from quantumion.compiler.flow.flowgraph import FlowGraph
from quantumion.compiler.math import MermaidMathExpr
from quantumion.compiler.analog.base import MermaidOperator

########################################################################################

__all__ = [
    "NetworkXFlowGraph",
    "MermaidFlowGraph",
    "markdown_flowgraph",
    "markdown_flowrules",
    "markdown_traversal",
]

########################################################################################


class NetworkXFlowGraph(Transformer):
    def visit_ForwardRules(self, model):
        G = nx.MultiDiGraph()

        G.add_node("start")
        return_nodes = []
        for n, rule in enumerate(model.rules):
            elements = self.visit(rule)

            if "forward_return" in rule.decorators:
                assert rule.name.startswith("forward_")
                node = rule.name[8:]
                return_nodes.append(node)

            if n == 0:
                G.add_edges_from([("start", elements["node"], {"label": ""})])

            G.add_node(elements["node"])
            G.add_edges_from(elements["edges"])

        for edge in G.edges:
            if edge[1] in return_nodes:
                G.add_edges_from(
                    [
                        (edge[1], edge[0], {"label": "return"}),
                    ]
                )

        return G

    def visit_ForwardRule(self, model):
        assert model.name.startswith("forward_")
        node = model.name[8:]
        edges = [
            (node, destination, {"label": key})
            for key, destination in model.destinations.items()
        ]
        if "forward_fixed_point" in model.decorators:
            edges += [
                (node, node, {"label": "repeat"}),
            ]

        return {
            "node": node,
            "edges": edges,
        }

    def visit_Traversal(self, model):
        G = nx.MultiDiGraph()

        G.add_node("start")
        current_element = None
        for n, site in enumerate(model.sites):
            next_element = self.visit(site)

            if n == 0:
                G.add_edges_from([("start", next_element["node"], {"label": ""})])

            G.add_node(next_element["node"])
            if current_element is not None:
                G.add_edges_from(
                    [
                        (
                            current_element["node"],
                            next_element["node"],
                            {"label": (current_element["site"], next_element["site"])},
                        )
                    ]
                )

            current_element = next_element

        return G

    def visit_TraversalSite(self, model):
        return dict(node=model.node, site=model.site)


########################################################################################


class MermaidFlowGraph(Transformer):
    def visit_ForwardRules(self, model):
        G = nx.MultiDiGraph()
        mermaid_string = "```mermaid\nstateDiagram-v2\n"

        G.add_node("start")
        return_nodes = []
        for n, rule in enumerate(model.rules):
            elements = self.visit(rule)

            if "forward_return" in rule.decorators:
                assert rule.name.startswith("forward_")
                node = rule.name[8:]
                return_nodes.append(node)

            if n == 0:
                G.add_edges_from([("start", elements["node"], {"label": ""})])
                mermaid_string += "\n[*] --> {}".format(elements["node"])

            G.add_node(elements["node"])
            G.add_edges_from(elements["edges"])

            mermaid_string += "".join(
                [
                    "\n{} --> {}: {}".format(edge[0], edge[1], edge[2]["label"])
                    for edge in elements["edges"]
                ]
            )

        for edge in G.edges:
            if edge[1] in return_nodes:
                G.add_edges_from(
                    [
                        (edge[1], edge[0], {"label": "return"}),
                    ]
                )
                mermaid_string += "\n{} --> {}: {}".format(edge[1], edge[0], "return")

        mermaid_string += "\n```\n"
        return mermaid_string

    def visit_ForwardRule(self, model):
        assert model.name.startswith("forward_")
        node = model.name[8:]
        edges = [
            (node, destination, {"label": key})
            for key, destination in model.destinations.items()
        ]
        if "forward_fixed_point" in model.decorators:
            edges += [
                (node, node, {"label": "repeat"}),
            ]

        return {
            "node": node,
            "edges": edges,
        }

    def visit_Traversal(self, model):
        mermaid_string = "```mermaid\nstateDiagram-v2\n"

        current_element = None
        for n, site in enumerate(model.sites):
            next_element = self.visit(site)

            if n == 0:
                mermaid_string += "\n[*] --> {}".format(next_element["node"])

            if current_element is not None:
                mermaid_string += "\n{} --> {}: {},{}".format(
                    current_element["node"],
                    next_element["node"],
                    current_element["site"],
                    next_element["site"],
                )

            current_element = next_element

        mermaid_string += "\n```\n"
        return mermaid_string

    def visit_TraversalSite(self, model):
        return dict(node=model.node, site=model.site, subtraversal=model.subtraversal)


########################################################################################


def markdown_flowrules(flowgraph, tabname="Main"):
    mermaid_string = '=== "{}"\n\t'.format(tabname.title())
    mermaid_string += "\n\t".join(
        flowgraph.forward_decorators.rules.accept(MermaidFlowGraph()).splitlines()
    )
    for node in flowgraph.nodes:
        if isinstance(node, FlowGraph):
            mermaid_string += "\n\t".join(
                ("\n" + markdown_flowrules(node, node.name) + "\n").splitlines()
            )
    return mermaid_string


def markdown_traversal(traversal, tabname="Main"):
    mermaid_string = '=== "{}"\n\t'.format(tabname.title())
    mermaid_string += "\n\t".join(traversal.accept(MermaidFlowGraph()).splitlines())
    for site in traversal.sites:
        if site.subtraversal:
            mermaid_string += "\n\t".join(
                (
                    "\n"
                    + markdown_traversal(
                        site.subtraversal,
                        tabname=f"{site.node} (Site {site.site})",
                    )
                    + "\n"
                ).splitlines()
            )
    return mermaid_string


def markdown_flowgraph(traversal, tabname="Main", prefix=""):
    md_string = '=== "{}"\n\t'.format(tabname.title())
    model = None
    for site in traversal.sites:
        if site.subtraversal:
            md_string += "\n\t".join(
                markdown_flowgraph(
                    site.subtraversal,
                    tabname=f"{site.node.title()} (Site {site.site})",
                    prefix=(prefix + "." if prefix else "") + site.node.title(),
                ).splitlines()
            )
            md_string += "\n\t"
            continue
        if site.model and model != site.model:
            md_string += f'=== "{prefix+"." if prefix else ""}{site.node.title()} (Site {site.site})"\n\t\t'
            if isinstance(site.model, MathExpr):
                md_string += "\n\t\t".join(
                    MermaidMathExpr().emit(site.model).splitlines()
                )
            if isinstance(site.model, Operator):
                md_string += "\n\t\t".join(
                    MermaidOperator().emit(site.model).splitlines()
                )
            md_string += "\n\t"
            model = site.model
    return md_string
