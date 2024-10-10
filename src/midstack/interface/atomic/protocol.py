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
    """
    Class representing a referenced optical channel/beam for the trapped-ion device.

    Attributes:
        transition: Transition that the optical channel/beam is referenced to.
        rabi: Rabi frequency of the referenced transition driven by the beam.
        detuning: Detuning away from the referenced transition.
        phase: Phase relative to the ion's clock.
        polarization: Polarization of the beam.
        wavevector: Wavevector of the beam.
        target: Index of the target ion of the beam.
    """

    transition: Transition
    rabi: CastMathExpr
    detuning: CastMathExpr
    phase: CastMathExpr
    polarization: conlist(float, max_length=2, min_length=2)
    wavevector: conlist(float, max_length=3, min_length=3)
    target: int


class Pulse(TypeReflectBaseModel):
    """
    Class representing the application of the beam for some duration.

    Attributes:
        beam: Optical channel/beam to turn on.
        duration: Period of time to turn the optical channel on for.

    """

    beam: Beam
    duration: float


class Protocol(TypeReflectBaseModel):
    """
    Class representing a light-matter interaction protocol/pulse program for the optical channels/beams.
    """

    pass


class ParallelProtocol(Protocol):
    """
    Class representing the parallel composition of a list of pulses or subprotocols.

    Attributes:
        sequence: List of pulses or subprotocols to compose together in a parallel fashion.
    """

    sequence: List[Union[Pulse, Protocol]]


class SequentialProtocol(Protocol):
    """
    Class representing the sequential composition of a list of pulses or subprotocols.

    Attributes:
        sequence: List of pulses or subprotocols to compose together in a sequntial fashion.
    """

    sequence: List[Union[Pulse, Protocol]]
