from quantumion.interface.analog.operator import *
from quantumion.interface.analog.dissipation import Dissipation
from quantumion.interface.analog.operations import *
from quantumion.compiler.analog.interface import *
from quantumion.backend.qutip.visitor import *
from quantumion.interface.math import MathStr
from quantumion.backend.metric import *
from quantumion.backend.task import Task, TaskArgsAnalog
from quantumion.backend import QutipBackend
from tests.test_analog.emulation.standard_protocols import *
import numpy as np
from rich import print as pprint
import unittest
from unittest_prettify.colorize import (
    colorize,
    GREEN,
    BLUE,
    RED,
    MAGENTA,
)
X, Y, Z, I, A, C, LI = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()

def get_amplitude_arrays(state: list):
    real_amplitudes, imag_amplitudes = [], []
    for x in state:
        real_amplitudes.append(x.real)
        imag_amplitudes.append(x.imag)
    return real_amplitudes, imag_amplitudes

class TestListClose(unittest.TestCase):
    def assertListsClose(self, list1, list2, tolerance=0.001):
        self.assertEqual(len(list1), len(list2), msg = "The input lists have different length")
        for elem1, elem2 in zip(list1, list2):
            self.assertAlmostEqual(elem1, elem2, delta=tolerance)

@colorize(color=MAGENTA)
class QutipEmulation(TestListClose, unittest.TestCase):
    maxDiff = None

    def test_one_qubit_rabi_flopping(self):
        """One qubit rabi flopping"""

        ac, args = one_qubit_rabi_flopping_protocol()

        task = Task(program = ac, args = args)

        backend = QutipBackend()

        results = backend.run(task = task)

        real_amplitudes, imag_amplitudes = get_amplitude_arrays(results.state)

        with self.subTest():
            self.assertListsClose(real_amplitudes, [-0.707, 0])
        with self.subTest():
            self.assertListsClose(imag_amplitudes, [0, 0.707])
        with self.subTest():
            self.assertAlmostEqual(results.metrics['Z'][-1], 0, delta=0.001)

    def test_bell_state_standard(self):
        """Standard Bell State preparation"""

        ac, args = bell_state_standard_protocol()

        task = Task(program = ac, args = args)

        backend = QutipBackend()

        results = backend.run(task = task)

        real_amplitudes, imag_amplitudes = get_amplitude_arrays(results.state)

        with self.subTest():
            self.assertListsClose(real_amplitudes, [0.707, 0, 0, 0.707])
        with self.subTest():
            self.assertListsClose(imag_amplitudes, [0, 0, 0, 0])
        with self.subTest():
            self.assertAlmostEqual(results.metrics['Z^0'][-1], 0, delta=0.001)
        with self.subTest():
            self.assertAlmostEqual(results.metrics['Z^1'][-1], 0, delta=0.001)

    def test_ghz_state(self):
        """Standard GHz State preparation"""

        ac, args = three_qubit_GHz_protocol()

        task = Task(program = ac, args = args)

        backend = QutipBackend()

        results = backend.run(task = task)

        real_amplitudes, imag_amplitudes = get_amplitude_arrays(results.state)

        with self.subTest():
            self.assertListsClose(real_amplitudes, [0.707, 0, 0, 0, 0, 0, 0, 0.707])
        with self.subTest():
            self.assertListsClose(imag_amplitudes, [0, 0, 0, 0, 0, 0, 0, 0])
        with self.subTest():
            self.assertAlmostEqual(results.metrics['Z^0'][-1], 0, delta=0.001)
        with self.subTest():
            self.assertAlmostEqual(results.metrics['Z^1'][-1], 0, delta=0.001)
        with self.subTest():
            self.assertAlmostEqual(results.metrics['Z^2'][-1], 0, delta=0.001)

if __name__ == '__main__':
    unittest.main()