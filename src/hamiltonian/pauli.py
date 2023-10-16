from quantumion.hamiltonian.base import Operator
from quantumion.hamiltonian.utils import tensor


class PauliBase(Operator):
    enum = None

    def __init__(self):
        super().__init__()
        self._data = [(1.0, {"qreg": [self.enum], "qmode": []})]

    @classmethod
    def tensor(cls, n: int, reg=None):
        """
        Constructs a tensor product over n local Hilbert spaces, with the Pauli class on the indices in `reg`.
        For unspecified registers, the identity is added.

        Example:
            `PauliX.tensor(3, [1, 2])` will result in the Pauli string
            :math:`\\mathcal{I} \\otimes \\sigma_x \\otimes \\sigma_x`
        """
        if reg is None:
            reg = list(range(n))

        if not all([r < n for r in reg]):
            raise ValueError("Register value outside the bounds.")

        local = [cls() if r in reg else PauliI() for r in range(n)]
        out = tensor(local)
        return out

    @classmethod
    def string(cls, paulis: list):
        """
        Constructs a tensor product of Pauli operators based on a list of strings

        Example:
        `Pauli.string(["x", "y", "z"])` will generate the operator term
        :math:`\\sigma_x \\otimes \\sigma_y \\otimes \\sigma_z`
        """
        m = dict(i=PauliI(), x=PauliX(), y=PauliY(), z=PauliZ())

        if not all([p in m.keys() for p in paulis]):
            raise ValueError("Register value outside the bounds.")

        local = [m[p] for p in paulis]
        out = tensor(local)
        return out


class PauliI(PauliBase):
    enum = 0

    def __init__(self):
        super().__init__()


class PauliX(PauliBase):
    enum = 1

    def __init__(self):
        super().__init__()


class PauliY(PauliBase):
    enum = 2

    def __init__(self):
        super().__init__()


class PauliZ(PauliBase):
    enum = 3

    def __init__(self):
        super().__init__()
