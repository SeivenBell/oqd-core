import json

from quantumion import __version__

"""
Statement classes:
"""


class Statement:
    def __init__(self):
        return


class Initialize(Statement):
    def __init__(self):
        super().__init__()
        return

    def __str__(self):
        return "initialize"


class Evolve(Statement):
    def __init__(self, name, time):
        super().__init__()
        self.name = name
        self.time = time
        return

    def __str__(self):
        return f"evolve {self.name} {self.time}"


class Measure(Statement):
    def __init__(self):
        super().__init__()
        return

    def __str__(self):
        return "measure"


"""
Main experiment class
"""


class Experiment:
    """

    """
    def __init__(self):
        super().__init__()

        self.ops = {}
        self.seq = []

    @property
    def dim_qreg(self):
        # todo: allow different Hilbert space sizes for subsequent operators
        _dim_ps = set([op.dim_qreg for op in self.ops.values()])
        assert len(_dim_ps) == 1, "Size of qreg Hilbert space not consistent."
        return list(_dim_ps)[0]

    @property
    def dim_qmode(self):
        # todo: allow different Hilbert space sizes for subsequent operators
        _dim_fs = set([op.dim_qmode for op in self.ops.values()])
        assert len(_dim_fs) == 1, "Size of qmode Hilbert space not consistent."
        return list(_dim_fs)[0]

    def check(self):
        for statement in self.seq:
            if isinstance(statement, Evolve):
                assert statement.name in self.ops.keys(), "Operator not listed."
            elif isinstance(statement, Measure):
                pass
            elif isinstance(statement, Initialize):
                pass

    def add(self, name, hamiltonian):
        self.ops[name] = hamiltonian

    def initialize(self):
        self.seq.append(Initialize())

    def evolve(self, name, time):
        self.seq.append(Evolve(name, time))

    def measure(self):
        self.seq.append(Measure())

    def serialize(self):
        s = f"OPENQSIM {__version__}"

        for identifier, op in self.ops.items():
            s += f"\ndefine {identifier} = {str(op)}"

        for statement in self.seq:
            s += f"\n{str(statement)}"
        return s

    def save(self, filename):
        # Open the file in write mode
        with open(filename, 'w') as file:
            file.write(self.serialize())

    def __str__(self):
        s = self.serialize()
        return s

