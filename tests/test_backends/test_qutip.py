from quantumion.hamiltonian.operator import *
from quantumion.hamiltonian.experiment import Experiment
from backends.qsim.qutip import QutipBackend, Data

from backends.base import Submission, Specification, Result


op = 4.0 * PauliX @ PauliY @ PauliZ @ PauliI @ (Creation * Annihilation) @ (Annihilation * Creation)
# print(op)


ex = Experiment()
ex.add(operator=PauliX @ PauliX)
# ex.add(operator=PauliY @ PauliX @ Creation @ Annihilation)
# print(ex)

spec = Specification(n_shots=100, fock_trunc=4, observables={})

result = Result()
data = Data()
print(data)

backend = QutipBackend()

submission = Submission(program=ex, specification=spec)
print(submission)

result = backend.run(submission)
print(result)
