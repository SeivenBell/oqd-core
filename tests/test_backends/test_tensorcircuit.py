#%%
from rich import print

from backends.digital.tc import TensorCircuitBackend
from backends.task import Task, TaskArgsDigital

from quantumion.digital.circuit import DigitalCircuit
from quantumion.digital.gate import Gate, H, CNOT
from quantumion.digital.statement import Statement, Measure, Barrier
from quantumion.digital.register import QuantumRegister, ClassicalRegister

#%%
qreg = QuantumRegister(id='q', reg=2)
creg = ClassicalRegister(id='c', reg=2)

circ = DigitalCircuit(qreg=qreg, creg=creg)
circ.add(H(qreg=qreg[0]))
circ.add(CNOT(qreg=qreg[0:2]))
# circ.add(Measure())
print(circ)

#%%
args = TaskArgsDigital(n_shots=10)
task = Task(program=circ, args=args)

#%%
backend = TensorCircuitBackend()
backend.run(task)

#%%
