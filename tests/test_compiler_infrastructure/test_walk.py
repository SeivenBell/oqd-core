import unittest
from unittest_prettify.colorize import (
    colorize,
    GREEN,
    RED,
    BLUE,
    MAGENTA,
)

from rich.console import Console

########################################################################################

from quantumion.compiler import *

########################################################################################


class PrintWalkOrder(RewriteRule):
    def __init__(self):
        self.current_index = 0
        self.string = ""

    def generic_map(self, model):
        self.string += f"\n{self.current_index}: {model}"
        self.current_index += 1
        pass


########################################################################################


@colorize(color=GREEN)
class TestPreWalk(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_pre(self):
        "Simple Test of Pre Walk"
        inp = ["a", ["b", "c"]]

        printer = Pre(PrintWalkOrder())

        printer(inp)
        assert (
            printer.children[0].string
            == "\n0: ['a', ['b', 'c']]\n1: a\n2: ['b', 'c']\n3: b\n4: c"
        )


########################################################################################


@colorize(color=RED)
class TestPostWalk(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_post(self):
        "Simple Test of Post Walk"
        inp = ["a", ["b", "c"]]

        printer = Post(PrintWalkOrder())

        printer(inp)
        assert (
            printer.children[0].string
            == "\n0: a\n1: b\n2: c\n3: ['b', 'c']\n4: ['a', ['b', 'c']]"
        )
