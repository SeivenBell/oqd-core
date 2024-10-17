from typing import Union

import unittest
from unittest_prettify.colorize import (
    colorize,
    GREEN,
    BLUE,
    RED,
    MAGENTA,
)

from oqd_compiler_infrastructure import Post, WalkBase, In, ConversionRule, RewriteRule

########################################################################################

from midstack.interface.analog import *
from midstack.interface.math import *
from midstack.compiler.analog.utils import PrintOperator
from midstack.compiler.analog.verify.operator import VerifyHilberSpaceDim

########################################################################################


def test_function(
    operator: Operator,
    rule: Union[ConversionRule, RewriteRule] = PrintOperator(verbose=True),
    walk_method: WalkBase = Post,
    reverse: bool = False,
):
    return walk_method(rule, reverse=reverse)(operator)


#######################################################


@colorize(color=BLUE)
class TestRealFinalStringVerbosePrintOp(unittest.TestCase):
    """Testing the final string produced with the actual for real number expressions"""

    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._rule = PrintOperator(verbose=True)

    def test_pauli_add_V(self):
        """Testing Vanilla Pauli Additions"""
        operator = PauliX() + PauliY() + PauliZ()
        actual = "(PauliX() + PauliY()) + PauliZ()"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_operator_multiply_V(self):
        """Testing Vanilla Pauli Multiplication  with verbose print"""
        operator = PauliX() * PauliY() * PauliZ()
        actual = "(PauliX() * PauliY()) * PauliZ()"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_scalar_left_multiplication_V(self):
        """Testing scalar Pauli left Multiplication"""
        operator = 3 * PauliX()
        actual = "(3) * PauliX()"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_scalar_left_multiple_multiplication_V(self):
        """Testing scalar Pauli left Multiplication with several terms"""
        operator = 3 * 5 * PauliX()
        actual = "(15) * PauliX()"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_scalar_right_multiplication_V(self):
        """Testing scalar Pauli right Multiplication"""
        operator = PauliX() * 3
        actual = "(3) * PauliX()"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_scalar_right_multiple_multiplication_V(self):
        """Testing scalar Pauli right Multiplication"""
        operator = PauliX() * 3 * 5
        actual = "(5) * ((3) * PauliX())"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_scalar_multiplication_with_addition_V(self):
        """Testing scalar Pauli Multiplication with addition"""
        operator = 3 * PauliX() + 5 * PauliI()
        actual = "((3) * PauliX()) + ((5) * PauliI())"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_scalar_multiplication_nested_l1_V(self):
        """Testing scalar Pauli Multiplication with nested operations"""
        operator = (PauliX() * 3) @ PauliY() + (5 * PauliZ()) @ (2 * PauliI())
        actual = "(((3) * PauliX()) @ PauliY()) + (((5) * PauliZ()) @ ((2) * PauliI()))"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_scalar_multiplication_nested_l2_V(self):
        """Testing scalar Pauli Multiplication with more nested operations with verbose print"""
        operator = (PauliX() * 3) @ ((3 * PauliY() + 7 * PauliY()) - (3 * PauliZ())) + (
            5 * 5 * PauliZ()
        ) @ (2 * PauliI())
        actual = "(((3) * PauliX()) @ ((((3) * PauliY()) + ((7) * PauliY())) - ((3) * PauliZ()))) + (((25) * PauliZ()) @ ((2) * PauliI()))"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_scalar_string_nested_float_combination_V(self):
        """Testing scalar Pauli multiplication with combination of string and (int, float) with verbose print"""
        operator = 3 * MathStr(string="4*t") * PauliX()
        actual = "(3 * (4 * t)) * PauliX()"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_kron_with_addition_V(self):
        """Testing tensor product with addition for Pauli with verbose print"""
        operator = PauliX() @ (PauliI() + PauliZ()) @ PauliY()
        actual = "(PauliX() @ (PauliI() + PauliZ())) @ PauliY()"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_string_left_multiplication_V(self):
        """Testing string Pauli left Multiplication"""
        operator = MathStr(string="sin(t)") * PauliX()
        actual = "(sin(t)) * PauliX()"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_string_right_multiplication_V(self):
        """Testing string Pauli right Multiplication"""
        operator = PauliX() * MathStr(string="cos(t)")
        actual = "(cos(t)) * PauliX()"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_string_left_right_multiplication_V(self):
        """Testing string Pauli left and right Multiplication with verbose print"""
        operator = MathStr(string="sin(t)") * PauliX() * MathStr(string="cos(t)")
        actual = "(cos(t)) * ((sin(t)) * PauliX())"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_string_left_right_multiplication_nested_V(self):
        """Testing string Pauli left and right nested Multiplication  with verbose print"""
        operator = (
            MathStr(string="sin(t)+3*tan(t)") * PauliX() * MathStr(string="cos(t)")
        )
        actual = "(cos(t)) * ((sin(t) + (3 * tan(t))) * PauliX())"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_minus_string_V(self):
        """Pauli scalar multiplication with string and with negative sign"""
        operator = 2 * MathStr(string="4*t") * -PauliX()
        actual = "(2 * (4 * t)) * ((-1) * PauliX())"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_multiple_minus_V(self):
        """Pauli scalar multiplication with string and with double negative  with verbose print"""
        operator = 2 * -(-PauliX())
        actual = "(2) * ((-1) * ((-1) * PauliX()))"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    @unittest.skip("Not Implemented")
    def test_pauli_multiple_minus_nested_V(self):
        raise NotImplementedError


@colorize(color=BLUE)
class TestComplexFinalStringVerbosePrintOp(unittest.TestCase):
    """Testing the final string produced with the actual for complex number expressions"""

    def __init__(self, methodName: str = "runTest") -> None:
        self._rule = PrintOperator(verbose=True)
        super().__init__(methodName)

    def test_pauli_left_img_V(self):
        """Testing Pauli with left img with verbose print"""
        operator = 2j * PauliX()
        actual = "(0.0 + (1j * 2.0)) * PauliX()"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_right_img_V(self):
        """Testing Pauli with right img  with verbose print"""
        operator = PauliX() * 2j
        actual = "(0.0 + (1j * 2.0)) * PauliX()"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)

    def test_pauli_nested_img_V(self):
        """Testing Pauli with nested img with verbose print"""
        operator = PauliX() * 2j * (PauliI() + 8j * PauliY())
        actual = "((0.0 + (1j * 2.0)) * PauliX()) * (PauliI() + ((0.0 + (1j * 8.0)) * PauliY()))"
        self.assertEqual(test_function(operator=operator, rule=self._rule), actual)


X, Y, Z, I, A, C, LI = (
    PauliX(),
    PauliY(),
    PauliZ(),
    PauliI(),
    Annihilation(),
    Creation(),
    Identity(),
)


@colorize(color=BLUE)
class TestHilbertSpaceDimVerification(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        self._rule = VerifyHilberSpaceDim()
        self._walk_method = In
        self._reverse = True
        super().__init__(methodName)

    def test_simple_addition_fail(self):
        """Addition fail"""
        op = 2 * (X @ Z @ Z) + 3 * (Y @ I) + 2 * (Z @ Z)
        self.assertRaises(
            AssertionError,
            lambda: test_function(
                operator=op,
                rule=self._rule,
                walk_method=self._walk_method,
                reverse=self._reverse,
            ),
        )

    def test_simple_addition_pass_single(self):
        """Addition pass single"""
        op = 2 * X + 3 * Y + Z + Y  # + 2 * (Z @ Z)
        test_function(
            operator=op,
            rule=self._rule,
            walk_method=self._walk_method,
            reverse=self._reverse,
        )

    def test_simple_addition_fail_single_with_ladder(self):
        """Addition fail single term with ladder"""
        op = 2 * X + Y + A + Z + Y  # + 2 * (Z @ Z)
        self.assertRaises(
            AssertionError,
            lambda: test_function(
                operator=op,
                rule=self._rule,
                walk_method=self._walk_method,
                reverse=self._reverse,
            ),
        )

    def test_simple_addition_fail_ladder(self):
        """Addition fail with ladder"""
        op = 2 * (X @ Z @ A) + 3 * (Y @ I @ C) + 2 * (Z @ Z @ (C * C * I) @ A)
        self.assertRaises(
            AssertionError,
            lambda: test_function(
                operator=op,
                rule=self._rule,
                walk_method=self._walk_method,
                reverse=self._reverse,
            ),
        )

    def test_simple_addition_pass_ladder(self):
        """Addition pass with ladder"""
        op = (
            2 * (X @ Z @ A)
            + (Y @ I @ C)
            + 2 * (Z @ Z @ (C * C * I))
            + (Y @ I @ (C * A * A * C * LI))
        )
        test_function(
            operator=op,
            rule=self._rule,
            walk_method=self._walk_method,
            reverse=self._reverse,
        )


#%%
if __name__ == "__main__":
    unittest.main()

#
# #%%
# X @ X
# X * X
# X @ (X * X + X)
#
# #%%
# 2 * X
# 2 * (X+X)


#%%