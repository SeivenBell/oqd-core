from pydantic import BaseModel, validator, field_validator, conint, ValidationError
from typing import List, Union, Literal, Optional


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

    def __getitem__(self, item):
        return self.reg[item]


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

    def __getitem__(self, item):
        return self.reg[item]


class UnitaryOp(BaseModel):
    id: str


class GateParameters(BaseModel):
    vals: list[Union[int, float]] = []


class Gate(BaseModel):
    uop: UnitaryOp
    qreg: Optional[Union[QuantumRegister, QuantumBit, int, list[int]]] = None
    creg: Optional[Union[ClassicalRegister, ClassicalBit, int, list[int]]] = None
    params: Optional[GateParameters] = None


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
    sequence: list[Union[Gate, Statement]] = []

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
            if len(ids) != len(set(ids)):
                raise ValidationError("Quantum register identifiers must be unique.")
        return v

    def add(self, op: Union[Gate, Statement]):
        self.sequence.append(op)

    def to_qasm(self):
        version = "2.0"
        qasm_str = f"OPENQASM {version};\n"

        for qreg in self.qreg:
            qasm_str += f"qreg {qreg.id}[{len(qreg.reg)}];\n"

        for creg in self.creg:
            qasm_str += f"creg {creg.id}[{len(creg.reg)}];\n"

        # for decl in self.declarations:
        #     qasm_str += ""

        for op in self.sequence:
            if isinstance(op, Gate):
                qasm_str += f"{op.uop.id}"
                print(op)
                qasm_str += ",".join([f"{qreg.id}[{qreg.index}]" for qreg in op.qreg])
                qasm_str += ";\n"

        return qasm_str


H = UnitaryOp(id="h")
CNOT = UnitaryOp(id="cx")
CX = UnitaryOp(id="cx")
CZ = UnitaryOp(id="cz")
X = UnitaryOp(id="x")


if __name__ == "__main__":
    qreg = QuantumRegister(id='q', reg=2)
    creg = ClassicalRegister(id='c', reg=2)

    circ = DigitalCircuit(qreg=qreg, creg=creg)
    print(circ)

    circ.add(Gate(uop=H, qreg=qreg[0]))
    circ.add(Gate(uop=H, qreg=qreg[1]))
    print(circ.sequence)

    # measure = Measure(qregs=qreg, cregs=cbits)
    # print(measure)

    print(circ.to_qasm())