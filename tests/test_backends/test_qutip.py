import numpy as np
import matplotlib.pyplot as plt
from rich import print as pprint

########################################################################################

from quantumion.interface.analog import (
    PauliX,
    PauliY,
    PauliZ,
    PauliI,
    AnalogCircuit,
    AnalogGate,
)

from quantumion.backend.analog.python.qutip import QutipBackend
from quantumion.backend.task import Task, TaskArgsAnalog
from quantumion.backend.metric import EntanglementEntropyVN, Expectation

########################################################################################

# %% example of creating an operator
op = (PauliY * PauliY) @ (PauliY * PauliX)  # @ (Creation * Annihilation)

# %% create an experiment to run/simulate
ex = AnalogCircuit()
gate = AnalogGate(
    duration=1.234,
    hamiltonian=[np.pi / 4 * PauliX @ PauliX, PauliY @ PauliY],
    dissipation=[],
)
ex.evolve(gate=gate)
gate = AnalogGate(duration=1.234, hamiltonian=[PauliX @ PauliI], dissipation=[])
ex.evolve(gate=gate)
pprint(ex)

# %% can serialize this to a JSON format...
json_str = ex.model_dump()
pprint(json_str)

# %% ... and then easily parse back into data tree
ex_parse = AnalogCircuit.model_validate(ex.model_dump())
pprint(ex_parse)

# %%
ex_parse = AnalogCircuit.model_validate(json_str)

# %% need another object that stores keywords about the backend runtime parameters
args = TaskArgsAnalog(
    n_shots=100,
    fock_cutoff=4,
    metrics={
        "ee_vn": EntanglementEntropyVN(qreg=[0]),
        "z": Expectation(operator=[0.5 * PauliZ @ PauliI, 0.5 * PauliI @ PauliZ]),
        "z1": Expectation(operator=[PauliZ @ PauliI]),
        "z2": Expectation(operator=[PauliI @ PauliZ]),
    },
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
for name, metric in result.metrics.items():
    ax.plot(result.times, metric, label=name)
ax.legend()
plt.show()

# %%
print(result.counts)
