# External imports
from typing import List, Union

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel
from quantumion.interface.atomic.system import System
from quantumion.interface.atomic.protocol import Protocol

########################################################################################

__all__ = [
    "AtomicCircuit",
]

########################################################################################


class AtomicCircuit(TypeReflectBaseModel):
    system: System
    protocol: Protocol
