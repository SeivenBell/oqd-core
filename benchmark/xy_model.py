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
circuit = AnalogCircuit()
gate = AnalogGate(
    duration=1.0,
    unitary=[np.pi / 4 * PauliX @ PauliX @ PauliX @ PauliX],
    dissipation=[]
)
circuit.add(gate=gate)

#%%
args = TaskArgsAnalog(
    n_shots=100,
    fock_cutoff=4,
    metrics={
        "ee_vn": EntanglementEntropyVN(qreg=[0, 1]),
        "z": Expectation(operator=[])
    },
    dt=0.1
)

task = Task(program=circuit, args=args)

#%%
backend = QutipBackend()
result = backend.run(task)

#%%
pprint(result)

#%%