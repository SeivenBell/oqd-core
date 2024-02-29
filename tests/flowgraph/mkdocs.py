import os

from pymdownx.superfences import fence_code_format

import yaml

########################################################################################

DEFAULT_MKDOCS_CONF = {
    "site_name": "Test",
    "site_description": "Test",
    "docs_dir": "resources",
    "nav": [
        {"Index": "index.md"},
    ],
    "use_directory_urls": False,
    "theme": {
        "name": "material",
        "palette": [
            {
                "media": "(prefers-color-scheme: light)",
                "scheme": "default",
                "primary": "light-blue",
                "accent": "orange",
                "toggle": {"icon": "material/lightbulb", "name": "Switch to dark mode"},
            },
            {
                "media": "(prefers-color-scheme: dark)",
                "scheme": "slate",
                "primary": "light-blue",
                "accent": "orange",
                "toggle": {
                    "icon": "material/lightbulb-outline",
                    "name": "Switch to light mode",
                },
            },
        ],
        "features": [
            "search.suggest",
            "search.highlight",
            "content.tabs.link",
            "navigation.indexes",
            "content.tooltips",
            "navigation.path",
            "content.code.annotate",
            "content.code.copy",
            "content.code.select",
        ],
    },
    "plugins": ["mkdocstrings"],
    "markdown_extensions": [
        {"toc": {"permalink": True, "toc_depth": 4}},
        {
            "pymdownx.highlight": {
                "anchor_linenums": True,
                "line_spans": "__span",
                "pygments_lang_class": True,
            }
        },
        "pymdownx.inlinehilite",
        "pymdownx.snippets",
        {"pymdownx.tabbed": {"alternate_style": True}},
        "admonition",
        "pymdownx.details",
        "pymdownx.blocks.admonition",
        "pymdownx.blocks.details",
        {
            "pymdownx.superfences": {
                "custom_fences": [
                    {
                        "name": "mermaid",
                        "class": "mermaid",
                        "format": fence_code_format,
                    }
                ]
            }
        },
        {"pymdownx.arithmatex": {"generic": True}},
    ],
    "extra_javascript": [
        "javascripts/mathjax.js",
        "https://polyfill.io/v3/polyfill.min.js?features=es6",
        "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
    ],
}


def graph_to_mkdocs(G, G2):
    folder = os.path.dirname(os.path.abspath(__file__))

    if not os.path.exists(os.path.join(folder, "resources")):
        os.makedirs(os.path.join(folder, "resources"))

    with open(os.path.join(folder, "resources/index.md"), mode="w") as f:
        f.write("# Content\n")

        n = 1
        for file in os.listdir(os.path.join(folder, "resources")):
            if file == "index.md":
                continue
            f.write(f"{n}. [{os.path.splitext(file)[0].title()}]({file})\n")
            n += 1

    with open(os.path.join(folder, "resources/forwardrules.md"), mode="w") as f:
        f.write("# ForwardRules\n")
        f.write(G)

    with open(os.path.join(folder, "resources/traversal.md"), mode="w") as f:
        f.write("# Traversal\n")
        f.write(G2)

    mkdocs_conf = DEFAULT_MKDOCS_CONF.copy()
    mkdocs_conf["nav"] += [
        {os.path.splitext(file)[0].title(): file}
        for file in os.listdir(os.path.join(folder, "resources"))
        if file != "index.md"
    ]

    with open(os.path.join(folder, "mkdocs.yml"), mode="w") as f:
        yaml.dump(mkdocs_conf, f)
