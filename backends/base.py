from pydantic import BaseModel

from typing import Union

########################################################################################

from quantumion.hamiltonian.experiment import Experiment
from quantumion.hamiltonian.operator import Operator
from quantumion.circuit.circuit import Circuit
from quantumion.atomic.schedule import Schedule

########################################################################################


class Specification(BaseModel):
    n_shots: int = 10
    fock_trunc: int = 4
    observables: dict[str, Operator] = {}
    dt: float = 0.1


class Result(BaseModel):
    counts: dict[int, int] = {}


class Submission(BaseModel):
    program: Union[Experiment, Circuit, Schedule]
    specification: Specification


########################################################################################


def run(submission, backend=None):
    if backend is None:
        from backends.qsim.qutip import QutipBackend
        backend = QutipBackend()

    print(f"Now running {submission}")
    backend = QutipBackend()
    result = backend.run(submission)
    return result
