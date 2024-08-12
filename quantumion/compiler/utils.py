from quantumion.compiler.base import PassBase

########################################################################################


def pass_tree(compiler: PassBase, level=0, *, print_fn=print):
    print_fn("  " * level + "- ", compiler, sep="")
    for c in compiler.children:
        pass_tree(c, level=level + 1, print_fn=print_fn)
    pass
