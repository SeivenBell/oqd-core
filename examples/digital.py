# %%
from rich import print as pprint
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

########################################################################################

from quantumion.interfaces.digital import (
    DigitalCircuit,
    H,
    CNOT,
    QuantumRegister,
    ClassicalRegister,
)

from quantumion.backend.task import Task, TaskArgsDigital
from quantumion.backend.digital.python.tc import TensorCircuitBackend

########################################################################################

# %%
qreg = QuantumRegister(id="q", reg=2)
creg = ClassicalRegister(id="c", reg=2)

circ = DigitalCircuit(qreg=qreg, creg=creg)
circ.add(H(qreg=qreg[0]))
circ.add(CNOT(qreg=qreg[0:2]))
pprint(circ)

# %%
args = TaskArgsDigital(n_shots=100)
task = Task(program=circ, args=args)

# %%
backend = TensorCircuitBackend()
result = backend.run(task)

# %%
pprint(result)

# %%
rho = np.outer(result.state, np.conj(result.state))
fig, axs = plt.subplots(1, 2)
sns.heatmap(rho.real, ax=axs[0])
sns.heatmap(rho.imag, ax=axs[1])
for ax in axs:
    ax.set_aspect("equal")
plt.show()

# %%
