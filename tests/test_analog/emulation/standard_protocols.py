from quantumion.interface.analog.operator import *
from quantumion.interface.analog.dissipation import Dissipation
from quantumion.interface.analog.operations import *
from quantumion.backend.task import TaskArgsAnalog
from quantumion.backend.metric import *
from quantumion.interface.math import MathStr
import numpy as np

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
