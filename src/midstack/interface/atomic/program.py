# External imports
from typing import List, Union

from oqd_compiler_infrastructure import TypeReflectBaseModel

########################################################################################

from .protocol import Protocol
from .register import Register

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
