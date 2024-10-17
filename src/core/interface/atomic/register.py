from typing import List

from oqd_compiler_infrastructure import TypeReflectBaseModel

########################################################################################

from .ion import Ion

########################################################################################

__all__ = [
    "Register",
]

########################################################################################


class Register(TypeReflectBaseModel):
    configuration: List[Ion]
