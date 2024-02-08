# External imports
from typing import List, Union

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel
from quantumion.interface.atomic.protocol import Protocol
from quantumion.interface.atomic.register import Register

########################################################################################

__all__ = [
    "Apply",
    "AtomicProgram",
]


########################################################################################


class Apply(TypeReflectBaseModel):
    protocol: Protocol
    time: float


########################################################################################


class AtomicProgram(TypeReflectBaseModel):
    statements: List[Union[Apply, Register]]
