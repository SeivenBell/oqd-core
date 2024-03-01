from typing import Any

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel

########################################################################################

__all__ = [
    "FlowOut",
]

########################################################################################


class FlowOut(TypeReflectBaseModel):
    model: Any
    emission: Any = None
