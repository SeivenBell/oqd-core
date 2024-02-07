# %%
from rich import print as pprint
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

########################################################################################

from quantumion.datastruct.analog import (
    PauliX,
    PauliY,
    PauliZ,
    PauliI,
    AnalogCircuit,
    AnalogGate,
)
from quantumion.backend.analog.python.qutip import QutipBackend
from quantumion.backend.analog.julia.quantumoptics import QuantumOpticsBackend
from quantumion.backend.task import Task, TaskArgsAnalog
from quantumion.backend.metric import Expectation, EntanglementEntropyVN

########################################################################################

# %%
ex = AnalogCircuit()
gate = AnalogGate(
    duration=3.0,
    hamiltonian=[np.pi * PauliX @ PauliY, np.pi * PauliI @ PauliX],
)
ex.evolve(gate=gate)


ex.model_dump_json()


# %%
args = TaskArgsAnalog(
    n_shots=100,
    fock_cutoff=4,
    metrics={
        "ee_vn": EntanglementEntropyVN(qreg=[0]),
        "z": Expectation(operator=[0.5 * PauliZ @ PauliI, 0.5 * PauliI @ PauliZ]),
    },
    dt=0.01,
)

task = Task(program=ex, args=args)

s = task.model_dump()
pprint(task)
c = Task(**s)

# %%
backends = {"quantumoptics": QuantumOpticsBackend(), "qutip": QutipBackend()}

# %%
results = {}

for key, backend in backends.items():
    for i in range(2):
        result = backend.run(task)
        results[key] = result

# %%
bases = result.counts.keys()
for basis in bases:
    print(
        f"Basis {basis} | Qutip {results['qutip'].counts[basis]} | QO {results['quantumoptics'].counts[basis]}"
    )


# %%
fig, axs = plt.subplots(2, 1)
for key, result in results.items():
    axs[0].plot(result.times, result.metrics["ee_vn"], label=key)
    axs[1].plot(result.times, result.metrics["z"], label=key)
    print(f"Backend {key} | counts = {result.counts}")

axs[0].set(ylabel=r"$S(\rho_A)$")
axs[1].set(ylabel=r"$\langle \sigma_z \rangle$")
axs[-1].set(xlabel="Time []")
axs[0].legend()
plt.show()
