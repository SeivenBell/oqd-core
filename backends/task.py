from dataclasses import dataclass, field
import numpy as np
from typing import Union, List, Optional, Dict
from pydantic_numpy import typing as pnd

from quantumion.types import ComplexFloat
from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.operator import Operator
from quantumion.digital.circuit import DigitalCircuit
from quantumion.atomic.schedule import AtomicProgram

from backends.base import TypeReflectBaseModel
from backends.metric import Metric
from backends.metric import Expectation, EntanglementEntropyVN, EntanglementEntropyReyni


@dataclass
class DataAnalog:
    times: np.array = field(default_factory=lambda: np.empty(0))
    state: np.array = field(default_factory=lambda: np.empty(0))
    metrics: dict[str, List[Union[float, int]]] = field(default_factory=dict)
    shots: np.array = field(default_factory=lambda: np.empty(0))


########################################################################################sss


class TaskArgsAnalog(TypeReflectBaseModel):
    n_shots: int = 10
    fock_cutoff: int = 4
    dt: float = 0.1
    metrics: Dict[str, Union[EntanglementEntropyVN, Expectation]] = {}


class TaskResultAnalog(TypeReflectBaseModel):
    counts: dict[int, int] = {}
    times: list[float] = []
    state: list[ComplexFloat] = None
    runtime: float = None
    metrics: dict[str, List[Union[float, int]]] = {}


########################################################################################


class TaskArgsDigital(TypeReflectBaseModel):
    repetitions: int = 10


class TaskResultDigital(TypeReflectBaseModel):
    counts: dict[str, int] = {}
    state: pnd.Np1DArray


########################################################################################


class TaskArgsAtomic(TypeReflectBaseModel):
    n_shots: int = 10
    fock_trunc: int = 4
    dt: float = 0.1


class TaskResultAtomic(TypeReflectBaseModel):
    # Hardware results
    collated_state_readout: dict[int, int] = {}
    state_readout: dict[int, int] = {}
    detector_counts: dict[int, pnd.NpNDArrayInt32] = {}


########################################################################################


class Task(TypeReflectBaseModel):
    program: Union[AnalogCircuit, DigitalCircuit, AtomicProgram]
    args: Union[TaskArgsAnalog, TaskArgsDigital, TaskArgsAtomic]
