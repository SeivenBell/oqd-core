#%%
from rich import print as pprint
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from quantumion.analog.operator import PauliX, PauliY, PauliZ, Creation, Annihilation, PauliI
from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.gate import AnalogGate
from backends.analog.python.qutip import QutipBackend
from backends.analog.julia.quantumoptics import QuantumOpticsBackend
from backends.task import Task, TaskArgsAnalog
from backends.metric import Expectation, EntanglementEntropyVN


#%%
ex = AnalogCircuit()
gate = AnalogGate(
    duration=1.0,
    unitary=[np.pi * PauliX @ PauliX],
    dissipation=[]
)
ex.add(gate=gate)



#%%
args = TaskArgsAnalog(
    n_shots=100,
    fock_cutoff=4,
    metrics={
        'a': EntanglementEntropyVN(qreg=[0]),
        'b': Expectation(operator=[PauliX @ PauliI])
    },
    dt=0.1
)

task = Task(program=ex, args=args)

s = task.model_dump()
pprint(task)
c = Task(**s)

#%%
backend = QuantumOpticsBackend()
# backend = QutipBackend()

#%%
result = backend.run(task)
pprint(result)
