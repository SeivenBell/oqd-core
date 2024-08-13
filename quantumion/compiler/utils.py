from quantumion.compiler.base import PassBase

########################################################################################

__all__ = [
    "pass_tree",
    "controlled_reverse",
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


def controlled_reverse(iterable, reverse, *, restore_type=False):
    new_iterable = reversed(iterable) if reverse else iterable
    new_iterable = iterable.__class__(new_iterable) if restore_type else new_iterable
    return new_iterable
