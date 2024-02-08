from typing import List

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel
from quantumion.interface.atomic import Transition

########################################################################################

__all__ = [
    "Pulse",
    "Protocol",
]

########################################################################################


class Pulse(TypeReflectBaseModel):
    transition: Transition
    rabi: float
    detuning: float
    phase: float
    polarization: List[float]
    wavevector: List[float]
    targets: List[int]


class Protocol(TypeReflectBaseModel):
    pulses: List[Pulse]
