from pydantic import BaseModel


class Op(BaseModel):
    qreg: list[int] = []
    creg: list[int] = []
    gate: str


class Circuit(BaseModel):
    sequence: list[Op] = []

    def add(self, op: Op):
        self.sequence.append(op)


H = Op(gate="h")
CNOT = Op(gate="h")


if __name__ == "__main__":
    circ = Circuit()
    circ.add(H)
    print(circ)