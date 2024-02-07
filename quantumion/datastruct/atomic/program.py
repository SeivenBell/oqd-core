# External imports
from typing import List, Union
from pydantic import ValidationError

########################################################################################

from quantumion.datastruct.base import TypeReflectBaseModel
from quantumion.datastruct.atomic.protocol import Protocol
from quantumion.datastruct.atomic.register import Register

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
