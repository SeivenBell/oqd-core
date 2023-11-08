#%%
from rich import print as pprint
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from quantumion.analog.operator import PauliX, PauliY, PauliZ, Creation, Annihilation
from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.gate import AnalogGate
from backends.analog.julia.quantumoptics import QuantumOpticsBackend
from backends.task import Task, TaskArgsAnalog


#%%
ex = AnalogCircuit()
gate = AnalogGate(
    duration=1.0,
    unitary=[np.pi * PauliX],
    dissipation=[]
)
ex.add(gate=gate)
pprint(type(ex.model_dump()))


#%%
args = TaskArgsAnalog(
    n_shots=100,
    fock_cutoff=4,
    observables={'z': PauliZ, 'x': PauliX, 'y': PauliY},
    dt=0.1
)

task = Task(program=ex, args=args)

#%%
backend = QuantumOpticsBackend()

#%%
result = backend.run(task)
pprint(result)

#%%
result

#%%