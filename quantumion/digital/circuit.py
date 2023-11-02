from pydantic import BaseModel, validator, field_validator, conint, ValidationError
from typing import List, Union, Literal


class QuantumBit(BaseModel):
    id: str
    index: conint(ge=0)  # a non-negative integer


class ClassicalBit(BaseModel):
    id: str
    index: conint(ge=0)  # a non-negative integer


class QuantumRegister(BaseModel):
    id: str = 'q'
    # regs: int
    reg: Union[List[QuantumBit], int]

    @field_validator('reg')
    def convert_reg(cls, v, values):
        if isinstance(v, int):
            id = values.data.get('id')
            v = [QuantumBit(id=id, index=i) for i in range(v)]
        return v


class ClassicalRegister(BaseModel):
    id: str = 'c'
    reg: Union[List[ClassicalBit], int]
    # regs: int

    @field_validator('reg')
    def convert_reg(cls, v, values):
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
    qreg: list[int]
    creg: list[int]
    params: GateParameters


class Statement(BaseModel):
    statement: str


class Barrier(BaseModel):
    statement: Literal['barrier'] = 'barrier'
    reg: Union[
        QuantumBit, QuantumRegister, List[QuantumRegister],
        ClassicalBit, ClassicalRegister, List[ClassicalRegister]
    ]


class Measure(BaseModel):
    statement: Literal['measure'] = 'measure'
    qreg: Union[QuantumBit, QuantumRegister]
    creg: Union[ClassicalBit, ClassicalRegister]


class DigitalCircuit(BaseModel):
    qreg: Union[int, QuantumRegister, list[QuantumRegister]] = None
    creg: Union[int, ClassicalRegister, list[ClassicalRegister]] = None

    declarations: list = []
    sequence: list[Op] = []

    @field_validator('creg')
    def convert_creg(cls, v):
        if isinstance(v, int):
            v = [ClassicalRegister(reg=v)]
        elif isinstance(v, ClassicalRegister):
            v = [v]

        if isinstance(v, list):
            ids = [creg.id for creg in v]
            if len(ids) != len(set(ids)):
                raise ValidationError("Classical register identifiers must be unique.")
        return v

    @field_validator('qreg')
    def convert_qreg(cls, v):
        if isinstance(v, int):
            v = [QuantumRegister(reg=v)]
        elif isinstance(v, QuantumRegister):
            v = [v]

        if isinstance(v, list):
            ids = [qreg.id for qreg in v]
            print(ids)
            if len(ids) != len(set(ids)):
                raise ValidationError("Quantum register identifiers must be unique.")
        return v

    def add(self, op: Op, *args):
        self.sequence.append(op)

    def to_qasm(self):
        version = "2.0"
        qasm_str = f"OPENQASM {version}\n"
        print(self.qreg)

        for qreg in self.qreg:
            qasm_str += f"qreg {qreg.id}[{len(qreg.reg)}];\n"

        for creg in self.creg:
            qasm_str += f"creg {creg.id}[{len(creg.reg)}];\n"

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
    qreg = QuantumRegister(id='q', reg=3)
    areg = QuantumRegister(id='a', reg=3)
    creg = ClassicalRegister(id='c', reg=3)

    # circ = Circuit(qreg=2, creg=2)
    circ = DigitalCircuit(qreg=[qreg, areg], creg=[creg])
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