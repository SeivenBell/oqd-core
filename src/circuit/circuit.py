from __future__ import annotations

import networkx as nx

from src.circuit.ops import Op, Hadamard


class CircuitBase:
    def __init__(self):

        return

    def to_qasm(self):
        return NotImplementedError


def h(circuit, qreg):
    circuit.add(Hadamard, qreg)


class Circuit(CircuitBase):
    """

    """
    def __init__(self, qregs, cregs):
        super().__init__()
        self.ops = []
        self.cregs = qregs
        self.qregs = cregs

        setattr(Circuit, "h", h)
        return

    def add(self, op, qregs=None, cregs=None):
        self.ops.append(op(qregs, cregs))


class CircuitDAG(CircuitBase):
    def __init__(self, qregs, cregs):
        super().__init__()
        self.qregs = qregs
        self.cregs = cregs
        self.dag = nx.MultiDiGraph()


class Register:
    def __init__(self, regs: int | list):
        if isinstance(regs, int):
            regs = [i for i in range(regs)]
        self.regs = regs
        super().__init__()
        return

    def __getitem__(self, item):
        return self.regs[item]


class ClassicalRegister(Register):
    def __init__(self, regs: int | list):
        super().__init__(regs)


class QuantumRegister(Register):
    def __init__(self, regs: int | list):
        super().__init__(regs)

        return


if __name__ == "__main__":
    qregs = QuantumRegister(1)
    cregs = ClassicalRegister(1)
    c = Circuit(qregs, cregs)
    for i in range(10):
        c.h(qregs[0])


    def to_qasm(circuit):
        fmap = {
            Hadamard: 'h'
        }

        header = "include QASM3.0"
        qasm = f"{header}\n"

        for op in circuit.ops:
            qasm += f"{fmap[op.__class__]} q {op.qregs}\n"

        return qasm

    qasm = to_qasm(c)
    print(qasm)