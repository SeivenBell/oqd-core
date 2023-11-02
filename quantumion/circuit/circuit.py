from pydantic import BaseModel


class Register(BaseModel):
    regs: list[int] = []


class Op(BaseModel):
    qreg: list[int] = []
    creg: list[int] = []
    gate: str


class Circuit(BaseModel):
    sequence: list[Op] = []

    def add(self, op: Op):
        self.sequence.append(op)


def h(circuit):
    circuit.add(Op(gate='h'))


setattr(Circuit, "h", h)
# H = Op(gate="h")
# CNOT = Op(gate="cx")


if __name__ == "__main__":
    circ = Circuit()
    circ.h()
    print(circ)
