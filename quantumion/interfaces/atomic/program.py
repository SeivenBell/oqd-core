# External imports
from typing import List, Union

########################################################################################

from quantumion.interfaces.base import TypeReflectBaseModel
from quantumion.interfaces.atomic.protocol import Protocol
from quantumion.interfaces.atomic.register import Register

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
