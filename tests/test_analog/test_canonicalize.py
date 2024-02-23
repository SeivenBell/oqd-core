from quantumion.interface.analog import *
from quantumion.compiler.analog.canonicalize import *
from quantumion.compiler.analog.base import *
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
X, Y, Z, I, A, C, LI = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()

def test_function(operator: Operator, visitor = PrintOperator()):
    return operator.accept(visitor=visitor)

class CanonicalFormErrors(unittest.TestCase):

    def assertCanonicalFormErrorRaised(self, operator, visitor = CanonicalizationVerificationOperator()):
        with self.assertRaises(CanonicalFormError) as context:
            test_function(operator = operator, visitor=visitor)
        print(context.exception)
    
    def assertCanonicalFormErrorNotRaised(self, operator, visitor = CanonicalizationVerificationOperator()):
        with self.assertRaises(AssertionError) as context:
            self.assertCanonicalFormErrorRaised(operator=operator, visitor=visitor)
        print(context.exception)

@colorize(color=MAGENTA)
class TestCanonicalizationVerification(CanonicalFormErrors, unittest.TestCase):
    maxDiff = None

    def test_simple_addition_true(self):
        """Simple addition test of canonical operator"""
        op =  1*I + 2*X
        #self.assertTrue(test_function(operator = op, visitor=CanonicalizationVerificationAddition()))
        self.assertCanonicalFormErrorNotRaised(operator=op)

    def test_simple_addition_tensor_prod_true(self):
        """Simple addition test of canonical operator with tensor product"""
        op =  1*(I@Y) + 2*(X@I)
        #self.assertTrue(test_function(operator = op, visitor=CanonicalizationVerificationAddition()))
        self.assertCanonicalFormErrorNotRaised(operator=op)

    def test_simple_addition_false(self):
        """Simple addition test of non canonical operator"""
        op =  1*I + X
        self.assertCanonicalFormErrorRaised(operator=op)

    def test_complicated_addition_true(self):
        """Complicated addition test of canonical operator"""
        op =  1*(I @ (A*A)) + 3*(X @ (A*A)) + 7*(Y @ (A*A)) + 6* (Z @ (A*A)) + 7 * (Z @ (A*C))
        self.assertCanonicalFormErrorNotRaised(operator=op)

    @unittest.skip("The issue of brackets seems to be resolved")
    def test_complicated_addition_passing_test_missing_bracket(self):
        # Note: removing some brackets gives errors because of tree structure what to do
        # This can be source of some ambiguity. 
        """Complicated addition test of canonical operator showing passing test with missing brackets"""
        op =  1*(I @ (A*A)) + 3*(X @ (A*A)) + 7*(Y @ A*A) + 6* (Z @ (A*A)) + 7 * (Z @ (A*C))
        self.assertCanonicalFormErrorNotRaised(operator=op)

    def test_complicated_addition_pass_with_all_bracket(self):
        """Complicated addition test of canonical operator without missing brackets"""
        op =  1*(I @ (A*A)) + 3*(X @ (A*A)) + 7*(Y @ (A*A)) + 6* (Z @ (A*A)) + 7 * (Z @ (A*C))
        self.assertCanonicalFormErrorNotRaised(operator=op)

    def test_complicated_addition_false(self):
        """Complicated addition test of non canonical operator"""
        op =  1*(I @ A*A) + 3*(X @ A*A) + 7*(Y @ A*A) + (Z @ A*A) + 7 * (Z @ A*C)
        self.assertCanonicalFormErrorRaised(operator=op)

    def test_pauli_tensor_and_ladder_multiplication_true(self):
        """Complicated pauli tensor product and ladder multiplication"""
        op = 2*(I @ (A*C) @ X @ (C*A*A*A*C*LI*A)) 
        self.assertCanonicalFormErrorNotRaised(operator=op)

    def test_pauli_tensor_and_ladder_multiplication_false_v1(self):
        """Complicated pauli tensor product and ladder multiplication with not in canonical form v1"""
        op = 2*(I @ (A*X) @ X @ (C*A*A*A*C*LI*A)) 
        self.assertCanonicalFormErrorRaised(operator=op)

    def test_pauli_tensor_and_ladder_multiplication_false_v2(self):
        """Complicated pauli tensor product and ladder multiplication with not in canonical form v2"""
        op = 2*(I @ (A*C) @ X @ (C*A*A*A*C*LI*A) @ (X * Y)) 
        self.assertCanonicalFormErrorRaised(operator=op)

    def test_pauli_tensor_and_ladder_multiplication_false_v3(self):
        """Complicated pauli tensor product and ladder multiplication with not in canonical form v3"""
        op = 2*(I @ (A*C) @ X @ (C*A*A*2*A*C*LI*A)) 
        self.assertCanonicalFormErrorRaised(operator=op)

    def test_scalar_operator_product_with_pauli(self): # produces `Incorrect canonical scalar operator multiplication` as expected
        """Nested product of Paulis"""
        op = (3*(3*(3*(A*A)))) + (2*(C*C))
        self.assertCanonicalFormErrorRaised(operator=op)

    def test_scalar_operator_product_with_ladder(self): # produces `Incorrect canonical scalar operator multiplication`` as expected
        """Nested product of Ladders"""
        op = (3*(3*(3*(X*Y)))) + (2*(X*Z))
        self.assertCanonicalFormErrorRaised(operator=op)
    
    def test_subtraction(self):
        op = 3*X - 2*Y
        self.assertCanonicalFormErrorRaised(operator=op)

    @unittest.skip("Not implemenyed yet")
    def test_proper(self):
        op = X @ (Y @ Z)
        self.assertCanonicalFormErrorRaised(operator=op)

@colorize(color=BLUE)
class TestGatherMathExpr(unittest.TestCase):
    maxDiff = None

    @unittest.skip("Not Implemented")
    def test_basic(self):
        raise NotImplementedError


@colorize(color=BLUE)
class TestCanonicalizationVerificationOperatorDistribute(CanonicalFormErrors, unittest.TestCase):
    maxDiff = None
    op = ((2*X) + Y) @ Z

    def test_pauli_simple_fail(self):
        """Simple failure with pauli"""
        op = ((2*X) + Y) @ Z
        self.assertCanonicalFormErrorRaised(operator=op, visitor=CanonicalizationVerificationOperatorDistribute())

    def test_pauli_ladder_simple_fail(self):
        """Simple failure with pauli and ladder"""
        op = ((2*X) + A) @ Z
        self.assertCanonicalFormErrorRaised(operator=op, visitor=CanonicalizationVerificationOperatorDistribute())

    def test_pauli_simple_pass(self):
        """Simple pass with pauli"""
        op = (2*X)@Z + Y@Z
        self.assertCanonicalFormErrorNotRaised(operator=op, visitor=CanonicalizationVerificationOperatorDistribute())

    def test_pauli_ladder_simple_pass(self):
        """Simple pass with pauli"""
        op = (2*X)@Z + Y@Z + 2*(A*A*A*C)*(C*A*A)
        self.assertCanonicalFormErrorNotRaised(operator=op, visitor=CanonicalizationVerificationOperatorDistribute())

    def test_pauli_nested_fail(self):
        """Simple failure with nested pauli"""
        op = Y*(X@(X@X*(X+X)))
        self.assertCanonicalFormErrorRaised(operator=op, visitor=CanonicalizationVerificationOperatorDistribute())

    def test_pauli_nested_pass(self):
        """Simple pass with nested pauli"""
        op  = 1*(I @ A*A) + 3*(X @ A*A) + 7*(Y @ A*A) + (Z @ A*A) + 7 * (Z @ A*C)
        self.assertCanonicalFormErrorNotRaised(operator=op, visitor=CanonicalizationVerificationOperatorDistribute())

    def test_complex_nested_pass(self):
        """Complicated pass with nested pauli and ladder"""
        op  = 1*(I @ A*A) + 3*(X @ A*A) + 7*(Y @ A*A) + (Z @ A*A*A*A*A*A*C+A*C*C*C) + 7 * (Z @ A*C)
        self.assertCanonicalFormErrorNotRaised(operator=op, visitor=CanonicalizationVerificationOperatorDistribute())

    def test_complex_nested_fail(self):
        """Complicated fail with nested pauli and ladder"""
        op  = 1*(I @ A*A) + 3*(X @ A*A) + 7*(Y @ A*A) + (Z @ (A*A*A*A*A*A*C+A*C*C*C)) + 7 * (Z @ A*C)
        self.assertCanonicalFormErrorRaised(operator=op, visitor=CanonicalizationVerificationOperatorDistribute())


if __name__ == '__main__':
    unittest.main()
    #node = 2 * PauliX() @ (2 * PauliY() * 3) @ (MathStr(string='5*t') * PauliZ()) + (2 * PauliY() +  3 * PauliY()) @ (MathStr(string='5*t') * PauliZ())
    # X, Y, Z, I = PauliX(), PauliY(), PauliZ(), PauliI()
    # node = X  @ Y @ Annihilation()@ Z
    # pprint(node)
    # pprint(node.accept(SeparatePauliLadder()))
    # #pprint(node.accept(GatherMathExpr()))
    # pprint(node.accept(DeNestOpMulKron()).accept(DeNestOpMulKron()).accept(GatherMathExpr()).accept(GatherMathExpr()).accept(GatherMathExpr()).accept(ProperKronOrder()).accept(SeparatePauliLadder()).accept(PrintOperator()))