#%%
from backends.digital.tc import TensorCircuitBackend
from backends.task import Task, TaskArgsDigital

from quantumion.digital.circuit import DigitalCircuit

#%%
circ = DigitalCircuit(qreg=2, creg=2)

#%%
args = TaskArgsDigital(n_shots=10)
task = Task(program=circ, args=args)

#%%
backend = TensorCircuitBackend()
backend.run(task)

#%%
