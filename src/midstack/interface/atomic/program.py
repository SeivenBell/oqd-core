# External imports
from typing import List, Union

########################################################################################

from midstack.interface.base import TypeReflectBaseModel
from midstack.interface.atomic.protocol import Protocol
from midstack.interface.atomic.register import Register

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
