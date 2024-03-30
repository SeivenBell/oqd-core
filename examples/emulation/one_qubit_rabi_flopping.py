import os
from quantumion.interface.analog.operator import *
from quantumion.interface.analog.dissipation import Dissipation
from quantumion.interface.analog.operations import *
from quantumion.compiler.analog.interface import *
from quantumion.backend.qutip.visitor import *
from quantumion.interface.math import MathStr
from quantumion.backend.metric import *
from quantumion.backend.task import Task, TaskArgsAnalog
import qutip as qt
import numpy as np
from rich import print as pprint
from quantumion.backend import QutipBackend
from examples.emulation.utils import plot_metrics_counts



if __name__ == "__main__":
    
    X, Y, Z, I, A, C, J = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()

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
        dt=1e-4,
    )

    task = Task(program = ac, args = args)

    backend = QutipBackend()

    experiment = backend.compile(task = task)
    pprint(experiment)

    results = backend.run(experiment = experiment)
    pprint(results)

    plot_metrics_counts(results = results, experiment_name = 'one-qubit-rabi-flopping.png')

