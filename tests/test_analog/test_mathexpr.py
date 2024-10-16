from typing import Union

import unittest
from unittest_prettify.colorize import (
    colorize,
    GREEN,
    BLUE,
    RED,
    MAGENTA,
)

from oqd_compiler_infrastructure import Post, Walk, ConversionRule, RewriteRule

########################################################################################

from midstack.compiler.math.rules import EvaluateMathExpr
from midstack.interface.math import *

########################################################################################


def test_function(
    math_str: str,
    rule: Union[ConversionRule, RewriteRule] = EvaluateMathExpr(),
    walk_method: Walk = Post,
):
    return walk_method(rule)(MathStr(string=math_str))


#######################################################
@colorize(color=BLUE)
class TestEvaluateMathExpr(unittest.TestCase):
    maxDiff = None

    def test_simple_addition(self):
        """Simple Addition"""
        inp = "3+5"
        actual = 8
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)

    def test_simple_addition_decimal(self):
        """Simple Addition with decimals"""
        inp = "3.02+5.01"
        actual = 8.03
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)

    def test_simple_sub(self):
        """Simple sub"""
        inp = "3-5"
        actual = -2
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)

    def test_simple_sub_decimal(self):
        """Simple sub with decimals"""
        inp = "-3.02+5.01"
        actual = 1.99
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)

    def test_simple_multiplication(self):
        """Simple multiplication"""
        inp = "3*5"
        actual = 15
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)

    def test_simple_div(self):
        """Simple div"""
        inp = "15/2"
        actual = 7.5
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)

    def test_simple_pow(self):
        """Simple power"""
        inp = "3**2.01"
        actual = 9.10
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)

    def test_simple_trig_sin(self):
        """Simple sine"""
        inp = "sin(0.25)"
        actual = 0.247
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)

    def test_simple_trig_tan(self):
        """Simple tangent"""
        inp = "tan(0.205)"
        actual = 0.208
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)

    def test_simple_complex(self):
        """Simple complex"""
        inp = "2*3 + 5*(1j)"
        actual = 6 + 5j
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)

    def test_nested_ops_1(self):
        """Complicated nested math operations"""
        inp = "1+2*3 + 9 - 0.1 + 7*(2+3*5+(10/3))"
        actual = 158.233
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)

    def test_nested_ops_trig(self):
        """Complicated nested math operations with trig"""
        inp = "sin(exp(2))"
        actual = 0.894
        self.assertAlmostEqual(first=test_function(inp), second=actual, delta=0.001)


if __name__ == "__main__":
    unittest.main()
