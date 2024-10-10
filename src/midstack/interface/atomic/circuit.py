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
    """
    Class representing a trapped-ion experiment in terms of light-matter interactons.

    Attributes:
        system: The trapped-ion system.
        protocol: Pulse program for the trapped-ion experiment referenced to the trapped-ion system.

    """

    system: System
    protocol: Protocol
