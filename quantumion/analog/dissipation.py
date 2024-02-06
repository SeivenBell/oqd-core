from typing import Union

from quantumion.base import VisitableBaseModel


class Dissipation(VisitableBaseModel):
    jumps: int = None  # todo: discuss ir for dissipation
