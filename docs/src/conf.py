# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import pathlib
import os
import shutil
import nbformat


sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent.absolute()))
print(str(pathlib.Path(__file__).parent.parent.absolute()))

project = 'OQD'
copyright = '2023, OQD'
author = 'Open Quanum Design'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration



templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

extensions = [
    "sphinx.ext.autodoc",
    # "sphinxcontrib.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "nbsphinx",
]

nbsphinx_custom_formats = {
    'default': ['nbsphinx-toctree-skip'],
}


# Display todos 
todo_include_todos = True

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'sphinx_material'
html_theme = 'furo'
# html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# latex settins
latex_elements = {
    'preamble': r'''
    \usepackage[utf8]{inputenc}
    ''',
}


def clear_notebook_output(notebook_path):
    with open(notebook_path, "r") as nb_file:
        nb_content = nb_file.read()

    nb = nbformat.reads(nb_content, as_version=4)

    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs = []

    with open(notebook_path, "w") as nb_file:
        nbformat.write(nb, nb_file)


def copy_notebooks(src_folder, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    notebook_files = [file for file in os.listdir(src_folder) if file.endswith(".ipynb")]

    for notebook_file in notebook_files:
        src_path = os.path.join(src_folder, notebook_file)
        dest_path = os.path.join(dest_folder, notebook_file)

        shutil.copy(src_path, dest_path)
        clear_notebook_output(dest_path)


source_folder = str(pathlib.Path(__file__).parent.parent.parent.joinpath('examples'))
destination_folder = str(pathlib.Path(__file__).parent.joinpath('notebooks'))

copy_notebooks(source_folder, destination_folder)
