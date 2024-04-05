from quantumion.interface.analog.operator import *
from quantumion.interface.analog.dissipation import Dissipation
from quantumion.interface.analog.operations import *
from quantumion.compiler.analog.interface import *
from quantumion.backend.qutip.visitor import *
from quantumion.interface.math import MathStr
from quantumion.backend.metric import *
from quantumion.backend.task import Task, TaskArgsAnalog
from quantumion.compiler.analog.base import PrintOperator
import qutip as qt
import numpy as np
from rich import print as pprint
from quantumion.backend import QutipBackend
from utils import plot_metrics_counts, tfim_hamiltonian
from functools import reduce


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

    n = 4

    # create field
    field = [[Z if i == j else I for i in range(n)] for j in range(n)]
    interaction = [X if i in (i, (i + 1) % n) else I for i in range(n)]

    field_hamiltonian, interaction_hamiltonian = tfim_hamiltonian(
        field=field, interaction=interaction
    )
    hamiltonian = field_hamiltonian + interaction_hamiltonian

    H = AnalogGate(hamiltonian=hamiltonian)

    ac = AnalogCircuit()
    ac.evolve(duration=1, gate=H)

    # define task args
    args = TaskArgsAnalog(
        n_shots=100,
        fock_cutoff=4,
        metrics={
            "Entanglement Entropy": EntanglementEntropyVN(qreg=[i for i in range(n//2)]),
        },
        dt=1e-2,
    )

    task = Task(program=ac, args=args)

    backend = QutipBackend()

    experiment = backend.compile(task=task)
    pprint(experiment)

    results = backend.run(experiment=experiment)
    pprint(results.state)

    plot_metrics_counts(results=results, experiment_name="tfim_{}_site.png".format(n))
