from pydantic import BaseModel
from typing import Union

from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.gate import AnalogGate
from quantumion.analog.operator import Operator

from quantumion.digital.circuit import DigitalCircuit
from quantumion.atomic.schedule import Schedule


class TaskArgs(BaseModel):
    n_shots: int = 10
    fock_trunc: int = 4
    observables: dict[str, Operator] = {}
    dt: float = 0.1


class TaskResult(BaseModel):
    counts: dict[int, int] = {}
    expect: dict[str, Union[float, int]] = {}
    times: list[float] = []


class Task(BaseModel):
    program: Union[AnalogCircuit, DigitalCircuit, Schedule]
    args: TaskArgs
