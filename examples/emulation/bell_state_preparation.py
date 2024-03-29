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
from examples.emulation.utils import amplitude, generate_complete_dictionary
import matplotlib.pyplot as plt
import seaborn as sns
colors = sns.color_palette(palette="Set2", n_colors=10)


if __name__ == "__main__":
    
    X, Y, Z, I, A, C, J = PauliX(), PauliY(), PauliZ(), PauliI(), Annihilation(), Creation(), Identity()

    # 1-qubit & 2-qubit Rabi frequencies
    w1 = 2 * np.pi * 1
    w2 = 2 * np.pi * 0.1

    Hx = AnalogGate(hamiltonian= w1 * (X @ I), dissipation=Dissipation())
    Hy = AnalogGate(hamiltonian= w1 * (Y @ I), dissipation=Dissipation())
    Hx_inv = AnalogGate(hamiltonian= -w1 * (X @ I), dissipation=Dissipation())
    Hy_inv = AnalogGate(hamiltonian= -w1 * (Y @ I), dissipation=Dissipation())
    Hxx = AnalogGate(hamiltonian= w2 * (X @ X), dissipation=Dissipation())

    ac = AnalogCircuit()

    # Hadamard
    ac.evolve(duration = np.pi / (2 * w1), gate = Hx)
    ac.evolve(duration = np.pi / (4 * w1), gate = Hy)

    # CNOT
    ac.evolve(duration = np.pi / (4 * w1), gate = Hy_inv)
    ac.evolve(duration = np.pi / (4 * w1), gate = Hx_inv)
    ac.evolve(duration = np.pi / (4 * w1), gate = Hx_inv)
    ac.evolve(duration = np.pi / (4 * w2), gate = Hxx)
    ac.evolve(duration = np.pi / (4 * w2), gate = Hy)

    #define task args
    args = TaskArgsAnalog(
        n_shots=100,
        fock_cutoff=4,
        metrics={
            "Z^0": Expectation(operator= (1*(Z@I))),
            "Z^1": Expectation(operator= (1*(I@Z))),
        },
        dt=1e-4,
    )

    task = Task(program = ac, args = args)

    backend = QutipBackend()

    experiment = backend.compile(task = task)
    pprint(experiment)

    results = backend.run(experiment = experiment)
    pprint(results)

    fig, axs = plt.subplots(3, 1, figsize=[8, 8])

    ax = axs[0]
    for k, (name, obs) in enumerate(results.metrics.items()):
        ax.plot(results.times, obs, label=f"$<{name}>$", color=colors[k])
    ax.legend()
    ax.set(xlabel="Time", ylabel="Expectation value")

    ax = axs[1]
    full_counts = generate_complete_dictionary(results.counts)
    x = list(full_counts.keys())
    
    ax.bar(x=x, height=amplitude(state = results.state), color=colors[2])
    ax.set(xlabel="Basis state", ylabel="Probability")

    ax = axs[2]
    x = list(full_counts.keys())
    counts = list(full_counts.values())

    ax.bar(x=x, height=counts, color=colors[2])
    ax.set(xlabel="Basis state", ylabel="Number of samples")

    fig.tight_layout()


    plot_directory = 'examples/emulation/plots/'

    if not os.path.exists(plot_directory):
        os.makedirs(plot_directory)
        
    dirname =  plot_directory + 'bell-state-preparation.png'
    plt.savefig(dirname)