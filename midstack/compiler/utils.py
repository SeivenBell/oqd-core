from midstack.compiler.base import PassBase

########################################################################################

__all__ = [
    "pass_tree",
]

########################################################################################


def pass_tree(compiler: PassBase, level=0, *, print_fn=print):
    """
    This is a utility function that prints the structure of a composite pass.
    """
    print_fn("  " * level + "- ", compiler, sep="")
    for c in compiler.children:
        pass_tree(c, level=level + 1, print_fn=print_fn)
    pass
