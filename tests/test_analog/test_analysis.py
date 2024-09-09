from midstack.interface.analog import *
from midstack.compiler.analog.analysis import TermIndex
from midstack.compiler.rule import RewriteRule
from midstack.compiler.walk import Walk, Post, Pre, In
import unittest
from midstack.interface.math import *
from unittest_prettify.colorize import (
    colorize,
    GREEN,
    BLUE,
    RED,
    MAGENTA,
)

X, Y, Z, I, A, C, LI = (
    PauliX(),
    PauliY(),
    PauliZ(),
    PauliI(),
    Annihilation(),
    Creation(),
    Identity(),
)


def test_function_TermIndex(operator: Operator):
    analysis = In(TermIndex())
    analysis(model=operator)
    return analysis.children[0].term_idx


@colorize(color=BLUE)
class TestTermIndex(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.rule = TermIndex()

    def test_simple_single_term_pauli(self):
        """Simple test single term pauli"""
        op = X + Y + Z + I
        expected = [[1], [2], [3], [0]]
        self.assertEqual(
            test_function_TermIndex(
                operator=op,
            ),
            expected,
        )

    def test_simple_single_term_ladder(self):
        """Simple test single term ladder"""
        op = A + C + LI
        expected = [[(1, 0)], [(1, 1)], [(0, 0)]]
        self.assertEqual(
            test_function_TermIndex(
                operator=op,
            ),
            expected,
        )

    def test_kron_add(self):
        """Simple kron add"""
        op = X @ Y + Z @ X + X @ X + Y @ Z
        expected = [[1, 2], [3, 1], [1, 1], [2, 3]]
        self.assertEqual(
            test_function_TermIndex(
                operator=op,
            ),
            expected,
        )

    def test_kron_single(self):
        """Simple kron single term"""
        op = X @ Y @ Z @ I
        expected = [[1, 2, 3, 0]]
        self.assertEqual(
            test_function_TermIndex(
                operator=op,
            ),
            expected,
        )

    def test_kron_single_ladder(self):
        """Simple kron single term with ladder"""
        op = C @ (A * LI)
        expected = [[(1, 1), (1, 0)]]
        self.assertEqual(
            test_function_TermIndex(
                operator=op,
            ),
            expected,
        )

    def test_kron_single_complicated(self):
        """Complicated kron single term"""
        op = X @ Y @ X @ X @ (A * C * A) @ I @ C
        expected = [[1, 2, 1, 1, (3, 1), 0, (1, 1)]]
        self.assertEqual(
            test_function_TermIndex(
                operator=op,
            ),
            expected,
        )

    def test_kron_add_complicated(self):
        """Complicated kron add"""
        op = X @ Y @ (C * LI * A * C) + X @ X + (A * C * A) @ I @ C + Y + Z
        expected = [[1, 2, (3, 2)], [1, 1], [(3, 1), 0, (1, 1)], [2], [3]]
        self.assertEqual(
            test_function_TermIndex(
                operator=op,
            ),
            expected,
        )

    def test_kron_add_complicated(self):
        """Complicated kron add with scalar mul"""
        op = C @ (C * LI * A * C) + 3 * (X @ X) + A * C * A + 3 * Y + 2 * Z + C + LI
        expected = [[(1, 1), (3, 2)], [1, 1], [(3, 1)], [2], [3], [(1, 1)], [(0, 0)]]
        self.assertEqual(
            test_function_TermIndex(
                operator=op,
            ),
            expected,
        )


if __name__ == "__main__":
    unittest.main()
