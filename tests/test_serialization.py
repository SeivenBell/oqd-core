import numpy as np

from pydantic import BaseModel

########################################################################################

from backends.task import Task, TaskArgsAnalog, TaskArgsDigital

from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.gate import *
from quantumion.analog.operator import *

from quantumion.digital.circuit import DigitalCircuit
from quantumion.digital.gate import H
from quantumion.digital.register import QuantumRegister, ClassicalRegister

########################################################################################


def serialization_test(x):
    x_json = x.model_dump()
    x_reserialized = x.__class__(**x_json)

    if x != x_reserialized:
        print(
            "{:<48}: {:<8}".format(
                "Serialization Test of {}".format(x.__class__.__name__), "Failed"
            )
        )
        return 0
    else:
        print(
            "{:<48}: {:<8}".format(
                "Serialization Test of {}".format(x.__class__.__name__), "Passed"
            )
        )
        return 1


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

    ########################################################################################

    g = globals().copy()

    for k, v in g.items():
        if isinstance(v, BaseModel):
            serialization_test(v)
