#%%
from rich import print as pprint
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pydantic import BaseModel
import networkx as nx

from quantumion.analog.operator import PauliX, PauliY, PauliZ, PauliI, Creation, Annihilation
from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.gate import AnalogGate
from quantumion.analog.math import tensor, prod, sum
from quantumion.utils.io import IO

from backends.task import Task, TaskArgsAnalog
from backends.analog.julia.quantumoptics import QuantumOpticsBackend
from backends.analog.python.qutip import QutipBackend
from backends.metric import *


#%%
def graph_to_operator(g):
    ops = []
    for edge in g.edges:
        op_x = tensor([PauliX if i in edge else PauliI for i in range(n_qreg)])
        # op_y = tensor([PauliZ if i in edge else PauliI for i in range(n_qreg)])
        ops.append(op_x)
        # ops.append(op_y)
    return ops


#%%
n_qreg = 4

gz = nx.grid_graph((n_qreg,), periodic=True)
ops = graph_to_operator(gz)

#%%
circuit = AnalogCircuit()
gate = AnalogGate(
    duration=4.0,
    unitary=ops,
    dissipation=[]
)
circuit.add(gate=gate)

#%%
z = [(1/n_qreg) * tensor([PauliZ if i==ind else PauliI for i in range(n_qreg)]) for ind in range(n_qreg)]
args = TaskArgsAnalog(
    n_shots=100,
    fock_cutoff=4,
    metrics={
        "ee_vn": EntanglementEntropyVN(qreg=[0]),
        "z": Expectation(operator=z)
    },
    dt=0.01
)

task = Task(program=circuit, args=args)

#%%
backend = QutipBackend()
result = backend.run(task)

#%%
pprint(result)

#%%
sns.set_theme(style="whitegrid")
fig, axs = plt.subplots(2, 1)
axs[0].plot(result.times, result.metrics['z'])
axs[1].plot(result.times, result.metrics['ee_vn'])
axs[0].set(xlabel='Time', ylabel=r'$\langle \sigma_z \rangle$')
axs[1].set(xlabel='Time', ylabel=r'$S(\rho_A)$')
fig.show()

#%%