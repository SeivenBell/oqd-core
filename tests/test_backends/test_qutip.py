import numpy as np
import matplotlib.pyplot as plt
from rich import print as pprint

from quantumion.analog.operator import PauliX, PauliY, PauliZ
from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.gate import AnalogGate

from backends.analog.python.qutip import QutipBackend
from backends.task import Task, TaskArgsAnalog


# %% example of creating an operator
op = (PauliY * PauliY) @ (PauliY * PauliX)  # @ (Creation * Annihilation)

# %% create an experiment to run/simulate
ex = AnalogCircuit()
gate = AnalogGate(duration=2.0, hamiltonian=[np.pi / 4 * PauliX], dissipation=[])
ex.evolve(gate=gate)
pprint(ex)

# %% can serialize this to a JSON format...
json_str = ex.model_dump()
pprint(json_str)

#%% ... and then easily parse back into data tree
ex_parse = AnalogCircuit.model_validate(ex.model_dump())
pprint(ex_parse)
#%%
# ex_parse = AnalogCircuit.model_validate(json_str)

# %% need another object that stores keywords about the backend runtime parameters
args = TaskArgsAnalog(
    n_shots=100,
    fock_cutoff=4,
    dt=0.01,
)

# %% we package the program (i.e. the experiment) and the specification together as one object
task = Task(program=ex, args=args)
print(task)

# %% we can now run this using the Qutip simulator
backend = QutipBackend()
result = backend.run(task)
print(result.model_fields_set)

# %%
fig, ax = plt.subplots()
for name, expect in result.expect.items():
    ax.plot(result.times, expect, label=name)
ax.legend()
plt.show()

# %%
