# External imports
from typing import List, Union

from oqd_compiler_infrastructure import TypeReflectBaseModel

########################################################################################

from .system import System
from .protocol import Protocol

########################################################################################

__all__ = [
    "AtomicCircuit",
]

########################################################################################


class AtomicCircuit(TypeReflectBaseModel):
    system: System
    protocol: Protocol
