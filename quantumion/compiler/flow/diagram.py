import networkx as nx

########################################################################################

from quantumion.compiler.visitor import Transformer

########################################################################################

__all__ = [
    "NetworkXFlowGraph",
    "MermaidFlowGraph",
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
