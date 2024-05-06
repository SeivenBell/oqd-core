from typing import Optional

from quantumion.interface.base import VisitableBaseModel

########################################################################################

__all__ = [
    "Dissipation",
]

########################################################################################


class Dissipation(VisitableBaseModel):
    jumps: Optional[int] = None  # todo: discuss ir for dissipation
