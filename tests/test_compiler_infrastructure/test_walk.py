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
from quantumion.interface.base import VisitableBaseModel

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

    def test_pre_list(self):
        "Test of Pre Walk on a list"
        inp = ["a", "b"]

        printer = Pre(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: ['a', 'b']\n1: a\n2: b")

    def test_pre_dict(self):
        "Test of Pre Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = Pre(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: {'a': 'a', 'b': 'b'}\n1: a\n2: b"
        )

    def test_pre_VisitableBaseModel(self):
        "Test of Pre Walk on a VisitableBaseModel"
        inp = {"a": "a", "b": "b"}

        class M(VisitableBaseModel):
            a: str
            b: str

        inp = M(a="a", b="b")

        printer = Pre(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a='a' b='b'\n1: a\n2: b")

    def test_pre_nested_list(self):
        "Test of Pre Walk on a nested list"
        inp = ["a", ["b", "c"]]

        printer = Pre(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: ['a', ['b', 'c']]\n1: a\n2: ['b', 'c']\n3: b\n4: c",
        )


########################################################################################


@colorize(color=RED)
class TestPostWalk(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_post_list(self):
        "Test of Post Walk on a list"
        inp = ["a", "b"]

        printer = Post(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a\n1: b\n2: ['a', 'b']")

    def test_post_dict(self):
        "Test of Post Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = Post(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: a\n1: b\n2: {'a': 'a', 'b': 'b'}"
        )

    def test_post_VisitableBaseModel(self):
        "Test of Post Walk on a VisitableBaseModel"
        inp = {"a": "a", "b": "b"}

        class M(VisitableBaseModel):
            a: str
            b: str

        inp = M(a="a", b="b")

        printer = Post(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a\n1: b\n2: a='a' b='b'")

    def test_post_nested_list(self):
        "Test of Post Walk on a nested list"
        inp = ["a", ["b", "c"]]

        printer = Post(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: a\n1: b\n2: c\n3: ['b', 'c']\n4: ['a', ['b', 'c']]",
        )


########################################################################################


@colorize(color=BLUE)
class TestLevelWalk(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_level_list(self):
        "Test of Level Walk on a list"
        inp = ["a", "b"]

        printer = Level(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: ['a', 'b']\n1: a\n2: b")

    def test_level_dict(self):
        "Test of Level Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = Level(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: {'a': 'a', 'b': 'b'}\n1: a\n2: b"
        )

    def test_level_VisitableBaseModel(self):
        "Test of Level Walk on a VisitableBaseModel"
        inp = {"a": "a", "b": "b"}

        class M(VisitableBaseModel):
            a: str
            b: str

        inp = M(a="a", b="b")

        printer = Level(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a='a' b='b'\n1: a\n2: b")

    def test_level_nested_list(self):
        "Test of Level Walk on a nested list"
        inp = [["a", ["b", "c"]], ["d", "e"]]

        printer = Level(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: [['a', ['b', 'c']], ['d', 'e']]\n1: ['a', ['b', 'c']]\n2: ['d', 'e']\n3: a\n4: ['b', 'c']\n5: d\n6: e\n7: b\n8: c",
        )


########################################################################################


@colorize(color=MAGENTA)
class TestInWalk(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def test_in_list(self):
        "Test of In Walk on a list"
        inp = ["a", "b"]

        printer = In(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a\n1: ['a', 'b']\n2: b")

    def test_in_dict(self):
        "Test of In Walk on a dict"
        inp = {"a": "a", "b": "b"}

        printer = In(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string, "\n0: a\n1: {'a': 'a', 'b': 'b'}\n2: b"
        )

    def test_in_VisitableBaseModel(self):
        "Test of In Walk on a VisitableBaseModel"
        inp = {"a": "a", "b": "b"}

        class M(VisitableBaseModel):
            a: str
            b: str

        inp = M(a="a", b="b")

        printer = In(PrintWalkOrder())

        printer(inp)
        self.assertEqual(printer.children[0].string, "\n0: a\n1: a='a' b='b'\n2: b")

    def test_in_nested_list(self):
        "Test of In Walk on a nested list"
        inp = [["a", ["b", "c"]], ["d", "e", "f"]]

        printer = In(PrintWalkOrder())

        printer(inp)
        self.assertEqual(
            printer.children[0].string,
            "\n0: a\n1: ['a', ['b', 'c']]\n2: b\n3: ['b', 'c']\n4: c\n5: [['a', ['b', 'c']], ['d', 'e', 'f']]\n6: d\n7: e\n8: ['d', 'e', 'f']\n9: f",
        )
