from typing import List, Union

from pydantic import conlist

from oqd_compiler_infrastructure import TypeReflectBaseModel

########################################################################################

from .system import Transition
from ..math import CastMathExpr

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
