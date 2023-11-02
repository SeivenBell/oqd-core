#%%
from rich import print as pprint
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from quantumion.analog.operator import PauliX, PauliY, PauliZ, PauliI
from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.gate import AnalogGate
from backends.analog.qutip import QutipBackend
from backends.task import Task, TaskArgsAnalog


#%% create an experiment to run/simulate
ex = AnalogCircuit()
gate = AnalogGate(
    duration=1.0,
    unitary=[np.pi / 4 * PauliX],
    dissipation=[]
)
ex.add(gate=gate)

#%% can serialize this to a JSON format...
json_str = ex.model_dump()

#%% ... and then easily parse back into data tree
ex_parse = AnalogCircuit(**json_str)

#%% need another object that stores keywords about the backend runtime parameters
args = TaskArgsAnalog(
    n_shots=100,
    fock_trunc=4,
    observables={'z': PauliZ, 'x': PauliX, 'y': PauliY},
    dt=0.1
)

#%% we package the program (i.e. the experiment) and the specification together as one object
task = Task(program=ex, args=args)
pprint(task)

#%% we can now run this using the Qutip simulator
backend = QutipBackend()
result = backend.run(task)

#%%
pprint(result)

#%%
fig, ax = plt.subplots()
for name, expect in result.expect.items():
    ax.plot(result.times, expect, label=name)
ax.legend()
plt.show()

#%%
rho = np.outer(result.state, np.conj(result.state))
fig, axs = plt.subplots(1, 2)
sns.heatmap(rho.real, ax=axs[0])
sns.heatmap(rho.imag, ax=axs[1])
for ax in axs:
    ax.set_aspect('equal')
plt.show()