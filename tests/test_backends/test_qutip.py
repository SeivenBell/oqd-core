#%%
import numpy as np

from quantumion.hamiltonian.operator import PauliX, PauliY, PauliZ, PauliI, Annihilation, Creation
from quantumion.hamiltonian.experiment import Experiment
from backends.qsim.qutip import QutipBackend, Data
from backends.base import Submission, Specification, Result

#%% example of creating an operator
op = np.pi * PauliX @ PauliX @ (Creation * Annihilation)
print(op)

#%% create an experiment to run/simulate
ex = Experiment()
ex.add(operator=np.pi/4 * PauliX @ PauliX)
print(ex)

#%% can serialize this to a JSON format...
json_str = ex.model_dump()
print(json_str)

#%% ... and then easily parse back into data tree
ex_parse = Experiment(**json_str)
print(type(ex_parse))
print(ex_parse)

#%% need another object that stores keywords about the backend runtime parameters
spec = Specification(n_shots=100, fock_trunc=4, observables={}, dt=0.1)

#%% we package the program (i.e. the experiment) and the specification together as one object
submission = Submission(program=ex, specification=spec)
print(submission)

#%% we can now run this using the Qutip simulator
backend = QutipBackend()
result = backend.run(submission)
print(result)

#%%
