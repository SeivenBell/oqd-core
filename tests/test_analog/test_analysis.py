from quantumion.interface.analog import *
from quantumion.compiler.analog.canonicalize import *
from quantumion.compiler.analog.verify import *
from quantumion.compiler.analog.error import *
from quantumion.compiler.analog.base import *
from quantumion.backend.task import Task, TaskArgsAnalog
from quantumion.backend.metric import Expectation
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

def test_function(node: Operator, visitor = PrintOperator()):
    return node.accept(visitor=visitor)

@colorize(color=BLUE)
class TestVerifyHilbertSpace(unittest.TestCase):
    maxDiff = None

    def __init__(self, methodName: str = "runTest") -> None:
        self._visitor = VerifyHilbertSpace()
        super().__init__(methodName)

    def test_simple_space_1_pass_1(self):
        """Addition pass for space_1 version 1"""
        op = X + Y + Z + I
        test_function(node=op, visitor=self._visitor)

    def test_simple_space_1_pass_2(self):
        """Addition pass for space_1 version 2"""
        op = X + Y
        test_function(node=op, visitor=self._visitor)

    def test_simple_single_term_pass_2(self):
        """Addition pass for single terms version 2"""
        op = X
        test_function(node=op, visitor=self._visitor)

    def test_simple_space_1_fail_1(self):
        """Addition fail for space_1 terms version 1"""
        op = X + A + Z + I
        self.assertRaises(AssertionError, lambda: test_function(node=op, visitor=self._visitor))

    def test_complicated_5_terms_pass(self):
        """Complicated nested assition pass"""
        op = (X@((X@Y@Y)+(Y@Z@I))@(Y+Z))+(X@Y@I@Z@I)+(X@Y@I@Z@I)
        test_function(node=op, visitor=self._visitor)

    def test_multiplication_pass(self):
        """Simple Multiplication pass"""
        op = X*X + Y*Y
        test_function(node=op, visitor=self._visitor)

    def test_multiplication_complicated_pass(self):
        """Multiplication complicated pass"""
        op = (X*X)@Y + Z@(Y*Y) + I@(I*Z)
        test_function(node=op, visitor=self._visitor)

    def test_multiplication_complicated_fail(self):
        """Multiplication complicated fail"""
        op = (X*X)@Y + Z@(Y*Y) + I@(I*Z)@Z
        self.assertRaises(AssertionError, lambda: test_function(node=op, visitor=self._visitor))

    def test_multiplication_fail(self):
        """Simple Multiplication fail"""
        op = X*A + Y*Y + 3*Z
        self.assertRaises(AssertionError, lambda: test_function(node=op, visitor=self._visitor))

    def test_multiplication_fail_annhiliation(self):
        """Simple Multiplication fail for incorrect addition"""
        op = X*I + Y*Y + A*C
        self.assertRaises(AssertionError, lambda: test_function(node=op, visitor=self._visitor))

    def test_complicated_5_terms_fail(self):
        """Complicated nested assition fail because of (X@Y@A@Z@I)"""
        op = (X@((X@Y@Y)+(Y@Z@I))@(Y+Z))+(X@Y@A@Z@I)+(X@Y@I@Z@I)
        self.assertRaises(AssertionError, lambda: test_function(node=op, visitor=self._visitor))

    def test_complicated_pass(self):
        """Nested complicated pass"""
        op = (X*X)@Y + Z@(Y*Y) + I@(I+Z) + (X*X*X*Y*Z)@(Z+I+Y)
        test_function(node=op, visitor=self._visitor)

    def test_complicated_scal_mul_padd(self):
        """Nested complicated pass with scalar mul"""
        op = (X*X)@Y + Z@(Y*(1*Y)) + 1*(I@(I+(1*Z))) + (X*X*X*Y*Z)@(Z+I+(1*Y))
        test_function(node=op, visitor=self._visitor)

    def test_complicated_fail(self):
        """Nested complicated fail"""
        op = (X*X)@Y + C@(Y*Y) + I@(I+Z) + (X*X*X*Y*Z)@(Z+I+Y)
        self.assertRaises(AssertionError, lambda: test_function(node=op, visitor=self._visitor))

    def test_complicated_scal_mul_fail(self):
        """Nested complicated fail with scalar mul"""
        op = (X*X)@Y + 1*(1*(C)@(Y*Y)) + I@(I+Z) + (X*X*X*Y*Z)@(Z+I+Y)
        self.assertRaises(AssertionError, lambda: test_function(node=op, visitor=self._visitor))

    def test_analog_gate_pass(self):
        "Test analog gate pass"
        gate = AnalogGate(hamiltonian=X@Y+ Z@I + I@Z)
        test_function(node=gate, visitor=self._visitor)

    def test_analog_gate_fail(self):
        "Test analog gate fail"
        gate = AnalogGate(hamiltonian=X@Y+ Z@A + I@Z)
        self.assertRaises(AssertionError, lambda: test_function(node=gate, visitor=self._visitor))

    def test_analog_circuit_pass(self):
        "Test analog circuit pass"
        ac = AnalogCircuit()
        gate1 = AnalogGate(hamiltonian=X@Y+ Z@I + I@Z)
        gate2 = AnalogGate(hamiltonian=X@Y+ Z@X + I@Z)
        ac.evolve(gate=gate1, duration=1)
        ac.evolve(gate=gate2, duration=1)
        test_function(node=ac, visitor=self._visitor)

    def test_analog_circuit_fail(self):
        "Test analog circuit fail"
        ac = AnalogCircuit()
        gate1 = AnalogGate(hamiltonian=X@Y+ Z@I + I@Z)
        gate2 = AnalogGate(hamiltonian=X@Y+ Z@A + I@Z)
        ac.evolve(gate=gate1, duration=1)
        ac.evolve(gate=gate2, duration=1)
        self.assertRaises(AssertionError, lambda: test_function(node=ac, visitor=self._visitor))

    def test_analog_circuit_fail_scalmul(self):
        "Test analog circuit fail with scalar mul"
        ac = AnalogCircuit()
        gate1 = AnalogGate(hamiltonian=X@Y+ Z@I + 2*(I@Z))
        gate2 = AnalogGate(hamiltonian=X@Y+ 1*(Z@A) + I@Z)
        ac.evolve(gate=gate1, duration=1)
        ac.evolve(gate=gate2, duration=1)
        self.assertRaises(AssertionError, lambda: test_function(node=ac, visitor=self._visitor))

    def test_analog_circuit_fail_inter_gates(self):
        "Test analog circuit fail inter gates"
        ac = AnalogCircuit()
        gate1 = AnalogGate(hamiltonian=X@Y+ Z@I + I@Z)
        gate2 = AnalogGate(hamiltonian=X@Y@Z+ Z@Z@Z + I@Z@Y)
        ac.evolve(gate=gate1, duration=1)
        ac.evolve(gate=gate2, duration=1)
        self.assertRaises(Exception, lambda: test_function(node=ac, visitor=self._visitor))

    def test_task_pass(self):
        "Test task pass simple"
        ac = AnalogCircuit()
        gate1 = AnalogGate(hamiltonian=X@Y+ Z@I + I@Z)
        ac.evolve(gate=gate1, duration=1)
        ac.evolve(gate=gate1, duration=1)
        args = TaskArgsAnalog(
            n_shots=500,
            fock_cutoff=4,
            metrics={
                "Z^0": Expectation(operator= Z@I),
                "Z^1": Expectation(operator= I@Z),
            },
            dt=1e-2,
        )
        task = Task(program=ac, args = args)
        test_function(node=task, visitor=self._visitor)

    def test_task_fail(self):
        "Test task fail among gates"
        ac = AnalogCircuit()
        gate1 = AnalogGate(hamiltonian=X@Y+ Z@I + I@Z)
        gate2 = AnalogGate(hamiltonian=X@Y@Z+ Z@I@I + I@Z@I)
        ac.evolve(gate=gate1, duration=1)
        ac.evolve(gate=gate2, duration=1)
        args = TaskArgsAnalog(
            n_shots=500,
            fock_cutoff=4,
            metrics={
                "Z^0": Expectation(operator= Z@I),
                "Z^1": Expectation(operator= I@Z),
            },
            dt=1e-2,
        )
        task = Task(program=ac, args = args)
        self.assertRaises(Exception, lambda: test_function(node=task, visitor=self._visitor))

    def test_task_fail_gates_task(self):
        "Test task fail between gates and task metrics"
        ac = AnalogCircuit()
        gate1 = AnalogGate(hamiltonian=X@Y+ Z@I + I@Z)
        gate2 = AnalogGate(hamiltonian=X@Z+ Z@I + 1*(I@I))
        ac.evolve(gate=gate1, duration=1)
        ac.evolve(gate=gate2, duration=1)
        args = TaskArgsAnalog(
            n_shots=500,
            fock_cutoff=4,
            metrics={
                "Z^0": Expectation(operator= Z@I@I),
                "Z^1": Expectation(operator= I@Z@I),
            },
            dt=1e-2,
        )
        task = Task(program=ac, args = args)
        self.assertRaises(ValueError, lambda: test_function(node=task, visitor=self._visitor))

    def test_task_fail_gates_task_scalmul(self):
        "Test task fail between gates and task metrics with scalar multiplication"
        ac = AnalogCircuit()
        gate1 = AnalogGate(hamiltonian=X@Y+ Z@I + I@Z)
        gate2 = AnalogGate(hamiltonian=X@Z+ (1*Z)@I + 1*(I@I))
        ac.evolve(gate=gate1, duration=1)
        ac.evolve(gate=gate2, duration=1)
        args = TaskArgsAnalog(
            n_shots=500,
            fock_cutoff=4,
            metrics={
                "Z^0": Expectation(operator= Z@I@I),
                "Z^1": Expectation(operator= I@(1*Z)@I),
            },
            dt=1e-2,
        )
        task = Task(program=ac, args = args)
        self.assertRaises(ValueError, lambda: test_function(node=task, visitor=self._visitor))

    def test_task_fail_multiplication(self):
        "Test task fail in gates for invalid operation"
        ac = AnalogCircuit()
        gate1 = AnalogGate(hamiltonian=X@Y+ Z@(I*A) + I@Z)
        gate2 = AnalogGate(hamiltonian=X@Y+ Z@I + I@Z)
        ac.evolve(gate=gate1, duration=1)
        ac.evolve(gate=gate2, duration=1)
        args = TaskArgsAnalog(
            n_shots=500,
            fock_cutoff=4,
            metrics={
                "Z^0": Expectation(operator= Z@I),
                "Z^1": Expectation(operator= I@Z),
            },
            dt=1e-2,
        )
        task = Task(program=ac, args = args)
        self.assertRaises(AssertionError, lambda: test_function(node=task, visitor=self._visitor))

    def test_task_fail_ladder(self):
        "Test task fail between gates and args for invalid ladder"
        ac = AnalogCircuit()
        gate1 = AnalogGate(hamiltonian=X@Y+ Z@I + I@Z)
        gate2 = AnalogGate(hamiltonian=X@Y+ Z@I + I@Z)
        ac.evolve(gate=gate1, duration=1)
        ac.evolve(gate=gate2, duration=1)
        args = TaskArgsAnalog(
            n_shots=500,
            fock_cutoff=4,
            metrics={
                "Z^0": Expectation(operator= Z@I),
                "Z^1": Expectation(operator= I@A),
            },
            dt=1e-2,
        )
        task = Task(program=ac, args = args)
        self.assertRaises(ValueError, lambda: test_function(node=task, visitor=self._visitor))

    def test_task_pass_annhiliation(self):
        "Test task fail between gates and args for invalid ladder"
        ac = AnalogCircuit()
        gate1 = AnalogGate(hamiltonian=X@A+ Z@LI + I@C)
        gate2 = AnalogGate(hamiltonian=X@A+ Z@C + I@LI)
        ac.evolve(gate=gate1, duration=1)
        ac.evolve(gate=gate2, duration=1)
        args = TaskArgsAnalog(
            n_shots=500,
            fock_cutoff=4,
            metrics={
                "Z^0": Expectation(operator = Z@LI),
                "Z^1": Expectation(operator = I@A),
            },
            dt=1e-2,
        )
        task = Task(program=ac, args = args)
        test_function(node=task, visitor=self._visitor)

if __name__ == '__main__':
    unittest.main()