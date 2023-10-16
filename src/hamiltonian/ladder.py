from __future__ import annotations

from quantumion.hamiltonian.base import Operator
from quantumion.hamiltonian.utils import tensor


class Ladder(Operator):
    enum = None
    """
    Creation and annihilation operators acting on a phonon mode
    :math:`a, a_\\dagger()`
    """

    def __init__(self):
        super().__init__()
        self._data = [(1.0, {"qreg": [], "qmode": [(self.enum,)]})]

    @classmethod
    def tensor(cls, n: int, reg: list | int | None = None, power=1) -> Operator:
        """
        Constructs an n-tensor product over of creation/annihilation operators on the indices `reg`.
        For unspecified registers, the identity is added.

        Example:
            `PauliX.tensor(3, [1, 2])` will result in the Pauli string
            :math:`\\mathcal{I} \\otimes \\sigma_x \\otimes \\sigma_x`
        """
        if reg is None:
            reg = list(range(n))

        if not all([r < n for r in reg]):
            raise ValueError("Register value outside the bounds.")

        if power == 0:
            c = Identity()
        elif power > 0:
            c = cls() ** power
        else:
            raise TypeError("Power must be a non-negative integer.")

        local = [c if r in reg else Identity() for r in range(n)]
        out = tensor(local)
        return out


class Creation(Ladder):
    enum = +1

    def __init__(self):
        super().__init__()


class Annihilation(Ladder):
    enum = -1

    def __init__(self):
        super().__init__()


class Identity(Ladder):
    enum = 0

    def __init__(self):
        super().__init__()
