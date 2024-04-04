from quantumion.interface.analog.operator import *
from quantumion.interface.analog.dissipation import Dissipation
from quantumion.interface.analog.operations import *
from quantumion.compiler.analog.interface import *
from quantumion.backend.qutip.visitor import *
from quantumion.interface.math import MathStr
from quantumion.backend.metric import *
from quantumion.backend.task import Task, TaskArgsAnalog
from quantumion.backend import QutipBackend
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

def one_qubit_rabi_flopping_protocol():

    Hx = AnalogGate(hamiltonian= -(np.pi / 4) * X, dissipation=Dissipation())

    ac = AnalogCircuit()
    ac.evolve(duration=1, gate=Hx)
    ac.evolve(duration=1, gate=Hx)
    ac.evolve(duration=1, gate=Hx)

    #define task args
    args = TaskArgsAnalog(
        n_shots=100,
        fock_cutoff=4,
        metrics={
            "Z": Expectation(operator= (1*(Z))),
        },
        dt=1e-3,
    )

    return ac, args

def bell_state_standard_protocol():

    Hii = AnalogGate(hamiltonian= 1*(I @ I), dissipation=Dissipation())
    Hxi = AnalogGate(hamiltonian= 1*(X @ I), dissipation=Dissipation())
    Hyi = AnalogGate(hamiltonian= 1*(Y @ I), dissipation=Dissipation())
    Hxx = AnalogGate(hamiltonian= 1*(X @ X), dissipation=Dissipation())
    Hmix = AnalogGate(hamiltonian= (-1)*(I @ X), dissipation=Dissipation())
    Hmxi = AnalogGate(hamiltonian= (-1)*(X @ I), dissipation=Dissipation())
    Hmyi = AnalogGate(hamiltonian= (-1)*(Y @ I), dissipation=Dissipation())

    ac = AnalogCircuit()

    # Hadamard
    ac.evolve(duration = (3 * np.pi) / 2, gate = Hii)
    ac.evolve(duration = np.pi / 2, gate = Hxi)
    ac.evolve(duration = np.pi / 4, gate = Hmyi)

    # CNOT
    ac.evolve(duration = np.pi / 4, gate = Hyi)
    ac.evolve(duration = np.pi / 4, gate = Hxx)
    ac.evolve(duration = np.pi / 4, gate = Hmix)
    ac.evolve(duration = np.pi / 4, gate = Hmxi)
    ac.evolve(duration = np.pi / 4, gate = Hmyi)
    ac.evolve(duration = np.pi / 4, gate = Hii)

    #define task args
    args = TaskArgsAnalog(
        n_shots=100,
        fock_cutoff=4,
        metrics={
            "Z^0": Expectation(operator= (1*(Z@I))),
            "Z^1": Expectation(operator= (1*(I@Z))),
        },
        dt=1e-2,
    )

    return ac, args

def three_qubit_GHz_protocol():

    # Hadamard on first qubit
    Hii = AnalogGate(hamiltonian= 1*(I @ I @ I), dissipation=Dissipation())
    Hxi = AnalogGate(hamiltonian= 1*(X @ I @ I), dissipation=Dissipation())
    Hyi = AnalogGate(hamiltonian= 1*(Y @ I @ I), dissipation=Dissipation())

    # CNOT on Second
    Hxx2 = AnalogGate(hamiltonian= 1*(X @ X @ I), dissipation=Dissipation())
    Hmix2 = AnalogGate(hamiltonian= (-1)*(I @ X @ I), dissipation=Dissipation())
    
    Hmxi = AnalogGate(hamiltonian= (-1)*(X @ I @ I), dissipation=Dissipation())
    Hmyi = AnalogGate(hamiltonian= (-1)*(Y @ I @ I), dissipation=Dissipation())

    # CNOT on Third
    Hxx3 = AnalogGate(hamiltonian= 1*(X @ I @ X), dissipation=Dissipation())
    Hmix3 = AnalogGate(hamiltonian= (-1)*(I @ I @ X), dissipation=Dissipation())
    ac = AnalogCircuit()

    # Hadamard
    ac.evolve(duration = (3 * np.pi) / 2, gate = Hii)
    ac.evolve(duration = np.pi / 2, gate = Hxi)
    ac.evolve(duration = np.pi / 4, gate = Hmyi)

    # CNOT
    ac.evolve(duration = np.pi / 4, gate = Hyi)
    ac.evolve(duration = np.pi / 4, gate = Hxx2)
    ac.evolve(duration = np.pi / 4, gate = Hmix2)
    ac.evolve(duration = np.pi / 4, gate = Hmxi)
    ac.evolve(duration = np.pi / 4, gate = Hmyi)
    ac.evolve(duration = np.pi / 4, gate = Hii)

    # CNOT
    ac.evolve(duration = np.pi / 4, gate = Hyi)
    ac.evolve(duration = np.pi / 4, gate = Hxx3)
    ac.evolve(duration = np.pi / 4, gate = Hmix3)
    ac.evolve(duration = np.pi / 4, gate = Hmxi)
    ac.evolve(duration = np.pi / 4, gate = Hmyi)
    ac.evolve(duration = np.pi / 4, gate = Hii)

    #define task args
    args = TaskArgsAnalog(
        n_shots=500,
        fock_cutoff=4,
        metrics={
            "Z^0": Expectation(operator= (1*(Z@I@I))),
            "Z^1": Expectation(operator= (1*(I@Z@I))),
            "Z^2": Expectation(operator= (1*(I@I@Z))),
        },
        dt=1e-2,
    )

    return ac, args

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


@colorize(color=BLUE)
class QutipCanonicalization(TestListClose, unittest.TestCase):
    maxDiff = None

    def test_one_qubit_rabi_flopping(self):
        """One qubit rabi flopping canonicalization"""

        _, args = one_qubit_rabi_flopping_protocol()

        Hx = AnalogGate(hamiltonian= -(np.pi / 8) * (2*X), dissipation=Dissipation())

        ac = AnalogCircuit()
        ac.evolve(duration=1, gate=Hx)
        ac.evolve(duration=1, gate=Hx)
        ac.evolve(duration=1, gate=Hx)

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
        """Standard Bell State preparation canonicalization"""

        _, args = bell_state_standard_protocol()

        Hii = AnalogGate(hamiltonian= 1*(I @ I), dissipation=Dissipation())
        Hxi = AnalogGate(hamiltonian= (X @ I), dissipation=Dissipation()) # Scalar Multiplication not given
        Hyi = AnalogGate(hamiltonian= 1*(Y @ I), dissipation=Dissipation())
        Hxx = AnalogGate(hamiltonian= 1*(X @ (I*X*I)), dissipation=Dissipation()) # multiplication by identity
        Hmix = AnalogGate(hamiltonian= (-1)*(I @ X), dissipation=Dissipation())
        Hmxi = AnalogGate(hamiltonian= (-1)*(X @ I), dissipation=Dissipation())
        Hmyi = AnalogGate(hamiltonian= (-0.5)*(Y @ (2*I)), dissipation=Dissipation()) # scalar multiplication

        ac = AnalogCircuit()

        # Hadamard
        ac.evolve(duration = (3 * np.pi) / 2, gate = Hii)
        ac.evolve(duration = np.pi / 2, gate = Hxi)
        ac.evolve(duration = np.pi / 4, gate = Hmyi)

        # CNOT
        ac.evolve(duration = np.pi / 4, gate = Hyi)
        ac.evolve(duration = np.pi / 4, gate = Hxx)
        ac.evolve(duration = np.pi / 4, gate = Hmix)
        ac.evolve(duration = np.pi / 4, gate = Hmxi)
        ac.evolve(duration = np.pi / 4, gate = Hmyi)
        ac.evolve(duration = np.pi / 4, gate = Hii)

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
if __name__ == '__main__':
    unittest.main()