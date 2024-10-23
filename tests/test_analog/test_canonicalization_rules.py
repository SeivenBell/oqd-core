# Copyright 2024 Open Quantum Design

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest_prettify.colorize import (
    colorize,
    BLUE,
    RED,
    MAGENTA,
)

from oqd_compiler_infrastructure import RewriteRule, WalkBase, Post, Pre, FixedPoint

########################################################################################

from oqd_core.interface.analog import *
from oqd_core.compiler.analog.rewrite.canonicalize import *
from oqd_core.interface.math import *

########################################################################################

X, Y, Z, I, A, C, LI = (
    PauliX(),
    PauliY(),
    PauliZ(),
    PauliI(),
    Annihilation(),
    Creation(),
    Identity(),
)


def test_function(operator: Operator, rule: RewriteRule, walk_method: WalkBase = Post):
    return FixedPoint(walk_method(rule))(operator)


@colorize(color=BLUE)
class TestOperatorDistribute(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.rule = OperatorDistribute()

    def test_simple(self):
        """Simple test"""
        op = X @ (X + Y)
        expected = X @ X + X @ Y
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)

    def test_no_effect(self):
        """Distribution does not do anything as GatherMathExpr required"""
        op = 2 * (X @ Y) * (3 * (I @ I))
        expected = 2 * (X @ Y) * (3 * (I @ I))
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)


@colorize(color=BLUE)
class TestGatherMathExpr(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.rule = GatherMathExpr()

    def test_simple(self):
        """Simple test"""
        op = X @ (3 * Y) + (2 * X) @ Z
        expected = 3 * (X @ Y) + 2 * (X @ Z)
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)

    def test_complicated(self):
        """Complicated test"""
        op = X @ (3 * Y * (3 * Z)) @ (10 * I) + (2 * X) @ Z @ (5 * Y)
        expected = (MathStr(string="3*3*10")) * ((X @ (Y * Z)) @ I) + MathStr(
            string="2*5"
        ) * (X @ Z @ Y)
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)

    def test_no_effect(self):
        """GatherMathExpr does not do anything as Distribution required"""
        op = X @ ((2 * X + 3 * Y))
        expected = X @ ((2 * X + 3 * Y))
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)


@colorize(color=BLUE)
class TestProperOrder(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.rule = ProperOrder()

    def test_simple(self):
        """Simple test"""
        op = X @ (Y @ (I @ Z))
        expected = ((X @ Y) @ I) @ Z
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)

    def test_complicated(self):
        """Complicated test with addition and scalar multiplication"""
        op = X @ (Y @ Z) + 3 * (Z @ (Y @ I))
        expected = (X @ Y) @ Z + 3 * ((Z @ Y) @ I)
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)


@colorize(color=BLUE)
class TestPauliAlgebra(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.rule = PauliAlgebra()

    def test_simple(self):
        """Simple test"""
        op = X * X + Y * Y + Z * I
        expected = I + I + Z
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)

    def test_nested_multiplications(self):
        """Nested Multiplication test"""
        op = X * X + Y * Y * Z * I
        expected = I + Z
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)

    def test_nested_multiplications_complicated(self):
        """Complicated Nested Multiplication test fails as we need GatherMathExpr after PauliAlgebra"""
        op = Z * X * X * Y * Y * Z * I
        expected = I + Z
        self.assertNotEqual(test_function(operator=op, rule=self.rule), expected)


@colorize(color=BLUE)
class TestGatherPauli(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.rule = GatherPauli()

    def test_simple(self):
        """Simple test"""
        op = X @ A @ Y
        expected = X @ Y @ A
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)

    def test_complicated(self):
        """Complicated test"""
        op = X @ A @ Y + (A * A * C) @ Y @ Z + X @ Y @ Z
        expected = X @ Y @ A + Y @ Z @ (A * A * C) + X @ Y @ Z
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)


@colorize(color=BLUE)
class TestNormalOrder(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.rule = NormalOrder()

    def test_simple(self):
        """Simple test"""
        op = (A * C) @ (A * C)
        expected = (C * A + LI) @ (C * A + LI)
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)

    def test_simple_fail(self):
        """Simple test fail as distribution required"""
        op = 1 * (A * A * C)
        expected = 1 * (C * A * A + LI * A + A * LI)
        self.assertNotEqual(test_function(operator=op, rule=self.rule), expected)

    def test_inside_pauli(self):
        """Simple test with Pauli"""
        op = X @ (A * C) @ Y
        expected = X @ (C * A + LI) @ Y
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)


@colorize(color=BLUE)
class TestPruneIdentity(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.rule = PruneIdentity()

    def test_simple(self):
        """Simple Test"""
        op = A * LI * C * LI * LI
        expected = A * C
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)

    def test_simple_nested(self):
        """Simple nested"""
        op = (A * LI * C * A * LI * C) @ LI @ (A * LI)
        expected = (A * C * A * C) @ LI @ (A)
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)


@colorize(color=BLUE)
class TestSortedOrder(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.rule = SortedOrder()

    def test_simple(self):
        """Simple Test"""
        op = X @ Y + X @ Z + I @ Z
        expected = I @ Z + X @ Y + X @ Z
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)

    def test_terminals(self):
        """Simple Test with terminals"""
        op = X + Z + Y + I
        expected = I + X + Y + Z
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)

    def test_ladder(self):
        """Simple Test with ladder"""
        op = X @ (C * A * A) + X @ (C * A)
        expected = X @ (C * A) + X @ (C * A * A)
        self.assertEqual(test_function(operator=op, rule=self.rule), expected)


@colorize(color=BLUE)
class TestScaleTerms(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.rule = ScaleTerms()

    def test_simple(self):
        """Simple test"""
        op = X @ (Y @ Z) + (Z @ (Y @ I))
        expected = MathStr(string="1") * (X @ (Y @ Z)) + MathStr(string="1") * (
            Z @ (Y @ I)
        )
        self.assertEqual(
            test_function(operator=op, rule=self.rule, walk_method=Pre), expected
        )

    def test_single_term(self):
        """Single term sorted order"""
        op = X @ (Y @ Z)
        expected = MathStr(string="1") * (X @ (Y @ Z))
        self.assertEqual(
            test_function(operator=op, rule=self.rule, walk_method=Pre), expected
        )

    def test_terminals(self):
        """Terminal term sorted order"""
        op = X + Y + Z + I
        expected = (
            MathStr(string="1") * X
            + MathStr(string="1") * Y
            + MathStr(string="1") * Z
            + MathStr(string="1") * I
        )
        self.assertEqual(
            test_function(operator=op, rule=self.rule, walk_method=Pre), expected
        )


if __name__ == "__main__":
    unittest.main()
