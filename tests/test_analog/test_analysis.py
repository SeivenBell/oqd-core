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
    GREEN,
    BLUE,
    RED,
    MAGENTA,
)

from oqd_compiler_infrastructure import RewriteRule, Post, Pre, In

########################################################################################


from oqd_core.interface.analog import *
from oqd_core.compiler.analog.analysis import TermIndex
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
