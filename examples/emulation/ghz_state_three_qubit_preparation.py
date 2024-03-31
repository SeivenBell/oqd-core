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
from examples.emulation.utils import plot_metrics_counts
import numpy as np

if __name__ == "__main__":
    
    X, Y, Z, I, A, C, J = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()

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

    task = Task(program = ac, args = args)

    backend = QutipBackend()

    experiment = backend.compile(task = task)
    #pprint(experiment)

    results = backend.run(experiment = experiment)
    pprint(results.state)

    plot_metrics_counts(results = results, experiment_name = 'ghz-state-3-qubit-preparation.png')