import numpy as np
import functools
import operator

from quantumion.interface.analog.operator import *
from quantumion.interface.analog.operations import *


X, Y, Z, I, A, C, J = (
    PauliX(),
    PauliY(),
    PauliZ(),
    PauliI(),
    Annihilation(),
    Creation(),
    Identity(),
)


def sum(args):
    return functools.reduce(operator.add, args)


def prod(args):
    return functools.reduce(operator.mul, args)


def tensor(args):
    return functools.reduce(operator.matmul, args)


def one_qubit_rabi_flopping():
    Hx = AnalogGate(hamiltonian=X)

    circuit = AnalogCircuit()
    circuit.evolve(duration=1, gate=Hx)
    return circuit


def bell_state_preparation():
    # 1-qubit & 2-qubit Rabi frequencies
    w1 = 2 * np.pi * 1
    w2 = 2 * np.pi * 0.1

    Hii = AnalogGate(hamiltonian=I @ I)
    Hxi = AnalogGate(hamiltonian=X @ I)
    Hyi = AnalogGate(hamiltonian=Y @ I)
    Hxx = AnalogGate(hamiltonian=X @ X)
    Hmix = AnalogGate(hamiltonian=(-1) * (I @ X))
    Hmxi = AnalogGate(hamiltonian=(-1) * (X @ I))
    Hmyi = AnalogGate(hamiltonian=(-1) * (Y @ I))

    circuit = AnalogCircuit()

    # Hadamard
    circuit.evolve(duration=(3 * np.pi) / 2, gate=Hii)
    circuit.evolve(duration=np.pi / 2, gate=Hxi)
    circuit.evolve(duration=np.pi / 4, gate=Hmyi)

    # CNOT
    circuit.evolve(duration=np.pi / 4, gate=Hyi)
    circuit.evolve(duration=np.pi / 4, gate=Hxx)
    circuit.evolve(duration=np.pi / 4, gate=Hmix)
    circuit.evolve(duration=np.pi / 4, gate=Hmxi)
    circuit.evolve(duration=np.pi / 4, gate=Hmyi)
    circuit.evolve(duration=np.pi / 4, gate=Hii)
    return


def ghz_state(n: int):
    if not isinstance(n, int) and n <= 2:
        raise ValueError("Number of qubits must be an integer greater than 2.")

    xi = tensor([X if i == 0 else I for i in range(n)])
    yi = tensor([Y if i == 0 else I for i in range(n)])

    circuit = AnalogCircuit()

    # evolve Hadamard gate
    circuit.evolve(duration=np.pi / 2, gate=AnalogGate(hamiltonian=xi))
    circuit.evolve(duration=np.pi / 4, gate=AnalogGate(hamiltonian=-1 * yi))

    for j in range(n):
        xx = tensor([X if i in (0, j) else I for i in range(n)])
        mix = -1 * tensor([X if i == j else I for i in range(n)])

        # CNOT
        circuit.evolve(duration=np.pi / 4, gate=AnalogGate(hamiltonian=yi))
        circuit.evolve(duration=np.pi / 4, gate=AnalogGate(hamiltonian=xx))
        circuit.evolve(duration=np.pi / 4, gate=AnalogGate(hamiltonian=mix))
        circuit.evolve(duration=np.pi / 4, gate=AnalogGate(hamiltonian=-xi))
        circuit.evolve(duration=np.pi / 4, gate=AnalogGate(hamiltonian=-yi))

    return circuit


def tfim(n: int):
    if not isinstance(n, int) and n > 2:
        raise ValueError("Number of qubits, n, must be an integer greater than 2.")

    field = sum([tensor([X if i == j else I for i in range(n)]) for j in range(n)])
    interaction = sum(
        [
            tensor([Z if j in (i, (i + 1) % n) else I for j in range(n)])
            for i in range(n)
        ]
    )

    hamiltonian = AnalogGate(hamiltonian=field + interaction)

    circuit = AnalogCircuit()
    circuit.evolve(duration=1, gate=hamiltonian)
    return circuit
