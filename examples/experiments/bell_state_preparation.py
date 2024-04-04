from quantumion.interface.analog.operator import *
from quantumion.interface.analog.dissipation import Dissipation
from quantumion.interface.analog.operations import *
from quantumion.compiler.analog.interface import *
from quantumion.backend.qutip.visitor import *
from quantumion.interface.math import MathStr
from quantumion.backend.metric import *
from quantumion.backend.task import Task, TaskArgsAnalog
from rich import print as pprint
from quantumion.backend import QutipBackend
from utils import plot_metrics_counts
import numpy as np


if __name__ == "__main__":

    X, Y, Z, I, A, C, J = (
        PauliX(),
        PauliY(),
        PauliZ(),
        PauliI(),
        Annihilation(),
        Creation(),
        Identity(),
    )

    # 1-qubit & 2-qubit Rabi frequencies
    w1 = 2 * np.pi * 1
    w2 = 2 * np.pi * 0.1

    Hii = AnalogGate(hamiltonian=1 * (I @ I), dissipation=Dissipation())
    Hxi = AnalogGate(hamiltonian=1 * (X @ I), dissipation=Dissipation())
    Hyi = AnalogGate(hamiltonian=1 * (Y @ I), dissipation=Dissipation())
    Hxx = AnalogGate(hamiltonian=1 * (X @ X), dissipation=Dissipation())
    Hmix = AnalogGate(hamiltonian=(-1) * (I @ X), dissipation=Dissipation())
    Hmxi = AnalogGate(hamiltonian=(-1) * (X @ I), dissipation=Dissipation())
    Hmyi = AnalogGate(hamiltonian=(-1) * (Y @ I), dissipation=Dissipation())

    ac = AnalogCircuit()

    # Hadamard
    ac.evolve(duration=(3 * np.pi) / 2, gate=Hii)
    ac.evolve(duration=np.pi / 2, gate=Hxi)
    ac.evolve(duration=np.pi / 4, gate=Hmyi)

    # CNOT
    ac.evolve(duration=np.pi / 4, gate=Hyi)
    ac.evolve(duration=np.pi / 4, gate=Hxx)
    ac.evolve(duration=np.pi / 4, gate=Hmix)
    ac.evolve(duration=np.pi / 4, gate=Hmxi)
    ac.evolve(duration=np.pi / 4, gate=Hmyi)
    ac.evolve(duration=np.pi / 4, gate=Hii)

    # define task args
    args = TaskArgsAnalog(
        n_shots=100,
        fock_cutoff=4,
        metrics={
            "Z^0": Expectation(operator=(1 * (Z @ I))),
            "Z^1": Expectation(operator=(1 * (I @ Z))),
        },
        dt=1e-2,
    )

    task = Task(program=ac, args=args)

    backend = QutipBackend()

    experiment = backend.compile(task=task)
    # pprint(experiment)

    results = backend.run(experiment=experiment)
    pprint(results.state)

    plot_metrics_counts(
        results=results, experiment_name="bell-state-preparation-standard.png"
    )
