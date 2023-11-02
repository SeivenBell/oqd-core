from pydantic import BaseModel, validator, field_validator, conint
from typing import List, Union, Literal


class QuantumBit(BaseModel):
    id: str
    index: conint(ge=0)  # a non-negative integer


class ClassicalBit(BaseModel):
    id: str
    index: conint(ge=0)  # a non-negative integer


class QuantumRegister(BaseModel):
    id: str = 'q'
    regs: Union[List[QuantumBit], int]

    @field_validator('regs')
    def convert_regs(cls, v, values):
        if isinstance(v, int):
            id = values.data.get('id')
            v = [QuantumBit(id=id, index=i) for i in range(v)]
        return v


class ClassicalRegister(BaseModel):
    id: str = 'c'
    regs: Union[List[ClassicalBit], int]

    @field_validator('regs')
    def convert_regs(cls, v, values):
        if isinstance(v, int):
            id = values.data.get('id')
            v = [ClassicalBit(id=id, index=i) for i in range(v)]
        return v


class Op(BaseModel):
    id: str


class GateParameters(BaseModel):
    vals: list[Union[int, float]] = []


class Gate(BaseModel):
    op: Op
    qregs: list[int]
    cregs: list[int]
    params: GateParameters


class Instruction(BaseModel):
    statement: str


# class Barrier(Instruction):
#     statement: str = "barrier"
#     qregs: Union[Quantum]

class Measure(Instruction):
    statement: Literal['measure'] = 'measure'
    qregs: Union[QuantumRegister, List[QuantumRegister]]
    cregs: Union[ClassicalRegister, List[ClassicalRegister]]


class Circuit(BaseModel):
    qregs: Union[int, QuantumRegister, list[QuantumRegister]] = None
    cregs: Union[int, ClassicalRegister, list[ClassicalRegister]] = None

    sequence: list[Op] = []
    declarations: list = []

    @field_validator('cregs')
    def convert_cregs(cls, v):
        if isinstance(v, int):
            v = ClassicalRegister(regs=v)
        return v

    @field_validator('qregs')
    def convert_qregs(cls, v):
        if isinstance(v, int):
            v = QuantumRegister(regs=v)
        return v

    def add(self, op: Op, *args):
        self.sequence.append(op)

    def to_qasm(self):
        version = "2.0"
        qasm_str = f"OPENQASM {version}"

        for qreg in self.qregs:
            qasm_str += f"{}"
        for decl in self.declarations:
            qasm_str += ""

        for op in self.sequence:
            qasm_str += ""

        return qasm_str


H = Op(id="h")
CNOT = Op(id="cx")
CX = Op(id="cx")
CZ = Op(id="cz")
X = Op(id="x")


if __name__ == "__main__":
    qbits = QuantumRegister(regs=3)
    cbits = ClassicalRegister(regs=3)

    circ = Circuit(qregs=2, cregs=2)
    print(circ)
    # circ.add()
    # print(qbits)
    # print(cbits)
    # print(circ)

    # print(QuantumRegister(regs=2))
    # print(ClassicalRegister(regs=2))
    # print(ClassicalRegister(id='a', regs=2))


    #
    # params = GateParameters()
    # print(params)
    #
    #
    # measure = Measure(qregs=qbits, cregs=cbits)
    # print(measure)

    print(circ.to_qasm())