from typing import Any, List, Optional

########################################################################################

from quantumion.interface.base import TypeReflectBaseModel

########################################################################################

__all__ = [
    "TraversalSite",
    "Traversal",
]

########################################################################################


class TraversalSite(TypeReflectBaseModel):
    site: str
    node: str
    nodetype: List[str]
    subtraversal: Optional["Traversal"] = None
    emission: Any = None
    model: Any = None


class Traversal(TypeReflectBaseModel):
    sites: List[TraversalSite] = []

    class Config:
        validate_assignment = True
