from dataclasses import dataclass, field
from typing import Union

from pydantic import BaseModel

import numpy as np

from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.gate import AnalogGate
from quantumion.analog.operator import Operator

from quantumion.digital.circuit import DigitalCircuit
from quantumion.atomic.schedule import Schedule

from backends.task import Task, TaskArgs, TaskResult


@dataclass
class DataAnalog:
    times: np.array = None
    state: np.array = None
    expect: dict[str, Union[int, float]] = field(default_factory=dict)
    shots: np.array = None


class TaskArgsAnalog(TaskArgs):
    n_shots: int = 10
    fock_trunc: int = 4
    observables: dict[str, Operator] = {}
    dt: float = 0.1


class TaskResultAnalog(TaskResult):
    counts: dict[int, int] = {}
    expect: dict[str, Union[float, int]] = {}
    times: list[float] = []
