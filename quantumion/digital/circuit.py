from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Union

from quantumion.digital.gate import Gate
from quantumion.digital.register import QuantumBit, QuantumRegister, ClassicalRegister
from quantumion.digital.statement import Statement, Measure, Barrier


class DigitalCircuit(BaseModel):
    qreg: List[QuantumRegister] = None
    creg: List[ClassicalRegister] = None

    declarations: List = []
    sequence: List[Union[Gate, Statement]] = []

    @field_validator('creg', mode='before')
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

    @field_validator('qreg', mode='before')
    def convert_qreg(cls, v):
        if isinstance(v, int):
            v = QuantumRegister(reg=v)
        elif isinstance(v, QuantumRegister):
            v = [v]
        if isinstance(v, list):
            ids = [qreg.id for qreg in v]
            if len(ids) != len(set(ids)):
                raise ValidationError("Quantum register identifiers must be unique.")

        return v

    def add(self, op: Union[Gate, Statement]):
        self.sequence.append(op)

    @property
    def qasm(self):
        version = "2.0"
        header = 'include "qelib1.inc";'

        qasm_str = f"OPENQASM {version};\n"
        qasm_str += f"{header};\n"

        for qreg in self.qreg:
            qasm_str += f"qreg {qreg.id}[{len(qreg.reg)}];\n"

        for creg in self.creg:
            qasm_str += f"creg {creg.id}[{len(creg.reg)}];\n"

        # for decl in self.declarations:
        #     qasm_str += ""

        for op in self.sequence:
            if isinstance(op, Gate):
                qasm_str += op.qasm
            elif isinstance(op, Statement):
                qasm_str += op.qasm

        return qasm_str


if __name__ == "__main__":
    from quantumion.digital.gate import H, CNOT

    qreg = QuantumRegister(id='q', reg=4)
    creg = ClassicalRegister(id='c', reg=2)

    circ = DigitalCircuit(qreg=qreg, creg=creg)
    print(circ)

    circ.add(H(qreg=qreg[0]))
    circ.add(CNOT(qreg=qreg[0:2]))
    circ.add(Measure())

    print(circ.sequence)
    # # # measure = Measure(qregs=qreg, cregs=cbits)
    # # # print(measure)
    # #
    print(circ.qasm)
