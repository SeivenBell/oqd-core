# %%
from rich import print

########################################################################################

from quantumion.interface.digital import (
    DigitalCircuit,
    H,
    CNOT,
    QuantumRegister,
    ClassicalRegister,
)

from quantumion.backend.digital.python.tc import TensorCircuitBackend
from quantumion.backend.task import Task, TaskArgsDigital

########################################################################################

# %%
qreg = QuantumRegister(id="q", reg=2)
creg = ClassicalRegister(id="c", reg=2)

circ = DigitalCircuit(qreg=qreg, creg=creg)
circ.add(H(qreg=qreg[0]))
circ.add(CNOT(qreg=qreg[0:2]))
# circ.add(Measure())
print(circ)

# %%
args = TaskArgsDigital(repetitions=10)
task = Task(program=circ, args=args)

# %%
backend = TensorCircuitBackend()
backend.run(task)

# %%
