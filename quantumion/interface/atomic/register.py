from typing import List

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel
from quantumion.interface.atomic import Ion

########################################################################################

__all__ = [
    "Register",
]

########################################################################################


class Register(TypeReflectBaseModel):
    configuration: List[Ion]
