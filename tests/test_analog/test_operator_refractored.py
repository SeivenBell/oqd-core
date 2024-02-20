from quantumion.interface.analog import *
from quantumion.compiler.analog.base import PrintOperator
from rich import print as pprint
import unittest
from quantumion.interface.math import *
from unittest_prettify.colorize import (
    colorize,
    GREEN,
    BLUE,
    RED,
    MAGENTA,
)


def test_function(operator: Operator, visitor = PrintOperator()) -> Operator:
    return operator.accept(visitor=visitor)

@colorize(color=BLUE)
class TestRealFinalString(unittest.TestCase):
    """Testing the final string produced with the actual for real number expressions"""
    maxDiff = None

    def test_pauli_add(self):
        """Testing Vanilla Pauli Additions"""
        inp = PauliX() + PauliY() + PauliZ()
        actual = "PauliX() + PauliY() + PauliZ()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_operator_multiply(self):
        """Testing Vanilla Pauli Multiplication"""
        inp = PauliX() * PauliY() * PauliZ()
        actual = "PauliX() * PauliY() * PauliZ()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_scalar_left_multiplication(self):
        """Testing scalar Pauli left Multiplication"""
        inp = 3*PauliX()
        actual = "(3) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_scalar_left_multiple_multiplication(self):
        """Testing scalar Pauli left Multiplication with several terms"""
        inp = 3 * 5 * PauliX()
        actual = "(15) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_scalar_right_multiplication(self):
        """Testing scalar Pauli right Multiplication"""
        inp = PauliX() * 3
        actual = "(3) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_scalar_right_multiple_multiplication(self):
        """Testing scalar Pauli right Multiplication"""
        inp = PauliX() * 3 * 5
        actual = "(5) * (3) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_scalar_multiplication_with_addition(self):
        """Testing scalar Pauli Multiplication with addition"""
        inp = 3*PauliX() + 5*PauliI()
        actual = "(3) * PauliX() + (5) * PauliI()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_scalar_multiplication_nested_l1(self):
        """Testing scalar Pauli Multiplication with nested operations"""
        inp = (PauliX() * 3) @ PauliY() + (5 * PauliZ()) @ (2 * PauliI())
        actual = "(3) * PauliX() @ PauliY() + (5) * PauliZ() @ (2) * PauliI()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_scalar_multiplication_nested_l2(self):
        """Testing scalar Pauli Multiplication with more nested operations"""
        inp = (PauliX() * 3) @ ((3*PauliY()+7*PauliY()) - (3 * PauliZ())) + (5*5 * PauliZ()) @ (2 * PauliI())
        actual = "(3) * PauliX() @ ((3) * PauliY() + (7) * PauliY() - (3) * PauliZ()) + (25) * PauliZ() @ (2) * PauliI()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_scalar_string_nested(self):
        """Testing scalar Pauli multiplication with combination of string and (int, float)"""
        inp = 3 * MathStr(string='4*t') * PauliX()
        actual = "(3 * 4 * t) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_kron_with_addition(self):
        """Testing tensor product with addition for Pauli"""
        inp = PauliX() @ (PauliI() + PauliZ()) @ PauliY()
        actual = "PauliX() @ (PauliI() + PauliZ()) @ PauliY()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_string_left_multiplication(self):
        """Testing string Pauli left Multiplication"""
        inp = MathStr(string='sin(t)')*PauliX()
        actual = "(sin(t)) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_string_right_multiplication(self):
        """Testing string Pauli right Multiplication"""
        inp = PauliX() * MathStr(string='cos(t)')
        actual = "(cos(t)) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_string_left_right_multiplication(self):
        """Testing string Pauli left and right Multiplication"""
        inp = MathStr(string='sin(t)') * PauliX() * MathStr(string='cos(t)')
        actual = "(cos(t)) * (sin(t)) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_string_left_right_multiplication_nested(self):
        """Testing string Pauli left and right nested Multiplication"""
        inp = MathStr(string='sin(t)+3*tan(t)') * PauliX() * MathStr(string='cos(t)')
        actual = "(cos(t)) * (sin(t) + 3 * tan(t)) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_minus_string(self):
        """Pauli scalar multiplication with string and with negative sign"""
        inp = 2 * MathStr(string='4*t') * -PauliX()
        actual = "(2 * 4 * t) * (-1) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_multiple_minus(self):
        """Pauli scalar multiplication with string and with double negative"""
        inp = 2 * -(-PauliX())
        actual = "(2) * (-1) * (-1) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    @unittest.skip("Not Implemented")
    def test_pauli_multiple_minus_nested(self):
        raise NotImplementedError

@colorize(color=MAGENTA)
class TestComplexFinalString(unittest.TestCase):
    """Testing the final string produced with the actual for complex number expressions"""
    def test_pauli_left_img(self):
        """Testing Pauli with left img"""
        inp = 2j*PauliX()
        actual = "(0.0 + 1j * 2.0) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_right_img(self):
        """Testing Pauli with right img"""
        inp = PauliX() * 2j
        actual = "(0.0 + 1j * 2.0) * PauliX()"
        self.assertEqual(test_function(inp), actual)

    def test_pauli_nested_img(self):
        """Testing Pauli with nested img"""
        inp = PauliX() * 2j * (PauliI() + 8j * PauliY())
        actual = "(0.0 + 1j * 2.0) * PauliX() * (PauliI() + (0.0 + 1j * 8.0) * PauliY())"
        self.assertEqual(test_function(inp), actual)



if __name__ == '__main__':
    unittest.main()
    # def s(elem):
    #     return MathExpr.cast(elem)


    # left =  2 * MathExpr.cast('4*t') * PauliX()
    # #left_cast =  2 * MathExpr.cast('4*t')* PauliX() # this works
    # pprint(left)
    # pprint(test_function(left))
    #pprint(left_cast)

