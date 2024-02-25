import itertools

########################################################################################

from quantumion.interface.base import VisitableBaseModel
from quantumion.interface.analog.operator import Operator
from quantumion.interface.analog.dissipation import Dissipation

########################################################################################

__all__ = [
    "AnalogGate",
]

########################################################################################


class AnalogGate(VisitableBaseModel):
    """
    Examples:
        >>> AnalogGate(duration=1.0, hamiltonian=[PauliX])

    Args:
        duration (float): the duration in microseconds to apply this analog gate
        hamiltonian (list[Operator]): the Hamiltonian to evolve the state under unitarily
        dissipation (list[Dissipation]): the dissipation terms to apply, represented as jump operators
    """

    duration: float
    hamiltonian: list[Operator] = []
    dissipation: list[Dissipation] = []

    @property
    def n_qreg(self):
        n = list(set([term.n_qreg for term in self.hamiltonian]))
        assert len(n) == 1
        return n[0]

    @property
    def n_qmode(self):
        n = list(set([term.n_qmode for term in self.hamiltonian]))
        assert len(n) == 1
        return n[0]
