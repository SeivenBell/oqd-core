from pydantic import field_validator, model_validator
from typing import List, Union

########################################################################################

from quantumion.interfaces.base import VisitableBaseModel
from quantumion.interfaces.digital.gate import Gate
from quantumion.interfaces.digital.register import QuantumRegister, ClassicalRegister
from quantumion.interfaces.digital.statement import Statement, Measure

########################################################################################

__all__ = [
    "DigitalCircuit",
]

########################################################################################


class DigitalCircuit(VisitableBaseModel):
    qreg: List[QuantumRegister] = []
    creg: List[ClassicalRegister] = []

    declarations: List = []
    sequence: List[Union[Gate, Statement]] = []

    class Config:
        extra = "forbid"

    @field_validator("creg", mode="before")
    @classmethod
    def convert_creg(cls, v):
        if isinstance(v, int):
            v = [ClassicalRegister(reg=v)]
        elif isinstance(v, ClassicalRegister):
            v = [v]
        return v

    @field_validator("qreg", mode="before")
    @classmethod
    def convert_qreg(cls, v):
        if isinstance(v, int):
            v = [QuantumRegister(reg=v)]
        elif isinstance(v, QuantumRegister):
            v = [v]
        return v

    @model_validator(mode="after")
    @classmethod
    def validate_ids(cls, data):
        ids = []
        for creg in data.creg:
            ids.append(creg.id)
        for qreg in data.qreg:
            ids.append(qreg.id)

        if len(ids) != len(set(ids)):
            raise ValueError(
                "Found multiple registers with the same identifier, register identifier must be unique"
            )

        return data

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
    from quantumion.interfaces.digital.gate import H, CNOT

    qreg = QuantumRegister(id="q", reg=4)
    creg = ClassicalRegister(id="c", reg=2)

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
