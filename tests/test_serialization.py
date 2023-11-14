import numpy as np

########################################################################################

from backends.task import Task, TaskArgsAnalog, TaskArgsDigital
from backends.provider import Provider

from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.gate import *
from quantumion.analog.operator import *

from quantumion.digital.circuit import DigitalCircuit
from quantumion.digital.gate import H, CNOT
from quantumion.digital.register import QuantumRegister, ClassicalRegister

########################################################################################


def serialization_test(x):
    x_json = x.model_dump()
    x_reserialized = x.__class__(**x_json)

    for n, i in enumerate((x, x_json, x_reserialized)):
        print("{:=^80}".format([" Original ", " JSON ", " Reserialized "][n]))
        print("{:<16}: {}".format(i.__class__.__name__, i))

    if x != x_reserialized:
        raise ValueError("Problem with reserialization")
    else:
        print("{:=^80}".format(" Reserialization Successful "))


########################################################################################

if __name__ == "__main__":
    op = np.pi * PauliX
    gate = AnalogGate(duration=1 / 4, unitary=[op], dissipation=[])
    ex = AnalogCircuit()
    ex.add(gate=gate)

    analog_args = TaskArgsAnalog(n_shots=10)
    analog_task = Task(program=ex, args=analog_args)

    ########################################################################################

    qreg = QuantumRegister(id="q", reg=2)
    creg = ClassicalRegister(id="c", reg=2)
    circ = DigitalCircuit(qreg=qreg, creg=creg)
    circ.add(H(qreg=qreg[0]))

    digital_args = TaskArgsDigital(n_shots=10)
    digital_task = Task(program=circ, args=digital_args)

    serialization_test(circ)
