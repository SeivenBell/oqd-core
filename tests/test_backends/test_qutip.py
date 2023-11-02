#%%
import numpy as np
import matplotlib.pyplot as plt

from quantumion.analog.operator import PauliX, PauliY, PauliZ, PauliI, Annihilation, Creation
from quantumion.analog.experiment import Experiment
from quantumion.analog.gate import AnalogGate
from backends.qsim.qutip import QutipBackend, Data
from backends.task import Task, TaskArgs, TaskResult

#%% example of creating an operator
op = ((PauliY * PauliY) @ (PauliY * PauliX)) #@ (Creation * Annihilation)

#%% create an experiment to run/simulate
ex = Experiment()
gate = AnalogGate(
    duration=2.0,
    unitary=[np.pi / 4 * PauliX],
    dissipation=[]
)
ex.add(gate=gate)

#%% can serialize this to a JSON format...
json_str = ex.model_dump()

#%% ... and then easily parse back into data tree
ex_parse = Experiment(**json_str)

#%% need another object that stores keywords about the backend runtime parameters
args = TaskArgs(n_shots=100, fock_trunc=4, observables={'z': PauliZ}, dt=0.01)

#%% we package the program (i.e. the experiment) and the specification together as one object
task = Task(program=ex, args=args)
print(task)

#%% we can now run this using the Qutip simulator
backend = QutipBackend()
result = backend.run(task)
print(result)

#%%
fig, ax = plt.subplots()
for name, expect in result.expect.items():
    ax.plot(result.times, expect, label=name)
ax.legend()
plt.show()

#%%