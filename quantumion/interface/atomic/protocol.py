from typing import List, Union

from pydantic import conlist

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel
from quantumion.interface.atomic.system import Transition
from quantumion.interface.math import *

########################################################################################

__all__ = [
    "Beam",
    "Pulse",
    "Protocol",
    "ParallelProtocol",
    "SequentialProtocol",
]

########################################################################################


class Beam(TypeReflectBaseModel):
    transition: Transition
    rabi: CastMathExpr
    detuning: CastMathExpr
    phase: CastMathExpr
    polarization: conlist(float, max_length=2, min_length=2)
    wavevector: conlist(float, max_length=3, min_length=3)
    target: int


class Pulse(TypeReflectBaseModel):
    beam: Beam
    duration: float


class Protocol(TypeReflectBaseModel):
    pass


class ParallelProtocol(Protocol):
    sequence: List[Union[Pulse, Protocol]]


class SequentialProtocol(Protocol):
    sequence: List[Union[Pulse, Protocol]]
