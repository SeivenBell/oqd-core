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
        CanonicalizationFlow2(name="canonicalization"),
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

    def mermaid_rules(flowgraph, tabname="Full"):
        mermaid_string = '=== "{}"\n\t'.format(tabname.title())
        mermaid_string += "\n\t".join(
            flowgraph.forward_decorators.rules.accept(MermaidFlowGraph()).splitlines()
        )
        for node in flowgraph.nodes:
            if isinstance(node, FlowGraph):
                mermaid_string += "\n" + mermaid_rules(node, node.name) + "\n"
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

    G = mermaid_rules(fg)
    G2 = mermaid_traversal(ft)

    ########################################################################################

    folder = "graph"
    if not os.path.exists(f"{folder}"):
        os.makedirs(f"{folder}")
    with open(f"{folder}/mkdocs.yml", mode="w") as f:
        mkdocs_config = """
site_name: Test
site_description: Test

docs_dir: "resources"

nav:
{}

use_directory_urls: false  # good for opening HTML files directly, but should be 'true' for deployment

theme:
  name: material

  palette:
  - media: '(prefers-color-scheme: light)'
    scheme: default
    primary: light-blue
    accent: orange
    toggle:
      icon: material/lightbulb
      name: Switch to dark mode
  - media: '(prefers-color-scheme: dark)'
    scheme: slate
    primary: light-blue
    accent: orange
    toggle:
      icon: material/lightbulb-outline
      name: Switch to light mode

  features:
  - search.suggest
  - search.highlight
  - content.tabs.link
  - navigation.indexes
  - content.tooltips
  - navigation.path
  - content.code.annotate
  - content.code.copy
  - content.code.select
#  - navigation.tabs

plugins:
  - mkdocstrings


markdown_extensions:
  - toc:
      permalink: true
      toc_depth: 4

  # for code snippets/syntax highlighting
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.tabbed:
      alternate_style: true

  # for notes/admonitions
  - admonition
  - pymdownx.details
  - pymdownx.blocks.admonition
  - pymdownx.blocks.details

  # for flow diagrams
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format

  - pymdownx.arithmatex:
      generic: true
extra_javascript:
  - javascripts/mathjax.js
  - https://polyfill.io/v3/polyfill.min.js?features=es6
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
        """.format(
            "\n".join(
                [
                    f"  - {os.path.splitext(file)[0].title()}: {file}"
                    for file in os.listdir(f"{folder}/resources")
                ]
            )
        )
        f.write(mkdocs_config)

    if not os.path.exists(f"{folder}/resources"):
        os.makedirs(f"{folder}/resources")
    with open(f"{folder}/resources/index.md", mode="w") as f:
        f.write("# Content\n")

        n = 1
        for file in os.listdir(f"{folder}/resources"):
            if file == "index.md":
                continue
            f.write(f"{n}. [{os.path.splitext(file)[0].title()}]({file})\n")
            n += 1
    with open(f"{folder}/resources/forwardrules.md", mode="w") as f:
        f.write("# ForwardRules\n")
        f.write(G)
    with open(f"{folder}/resources/traversal.md", mode="w") as f:
        f.write("# Traversal\n")
        f.write(G2)
