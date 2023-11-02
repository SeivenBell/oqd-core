from pydantic import BaseModel
from typing import Union

from quantumion.analog.experiment import Experiment
from quantumion.analog.gate import AnalogGate
from quantumion.circuit.circuit import Circuit
from quantumion.atomic.schedule import Schedule


class Specification(BaseModel):
    n_shots: int = 10
    fock_trunc: int = 4
    observables: dict[str, AnalogGate] = {}
    dt: float = 0.1


class Result(BaseModel):
    counts: dict[int, int] = {}


class Submission(BaseModel):
    program: Union[Experiment, Circuit, Schedule]
    specification: Specification
