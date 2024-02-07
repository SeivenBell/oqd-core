import numpy as np

from pydantic import BaseModel

import argparse

########################################################################################

from quantumion.datastruct.analog import *
from quantumion.datastruct.digital import *

from quantumion.backend.task import Task, TaskArgsAnalog, TaskArgsDigital

########################################################################################


def serialization_test(key, value, *, verbose=False):
    value_json = value.model_dump()
    value_reserialized = value.__class__(**value_json)

    if value != value_reserialized:
        print(
            "Serialization Test: {:^24}  {:^32} {:^8}".format(
                key,
                value.__class__.__name__,
                "Failed",
            )
        )
        if verbose:
            print("{:-^80}".format(" Original "))
            print(value)
            print("{:-^80}".format(" Reserialized "))
            print(value_reserialized)
            print("{:-^80}".format(""))
        return 0
    else:
        print(
            "Serialization Test: {:^24}  {:^32} {:^8}".format(
                key,
                value.__class__.__name__,
                "Passed",
            )
        )
        return 1


########################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="verbosity",
    )

    args = parser.parse_args()

    verbose = args.verbose

    ########################################################################################

    op = np.pi * PauliX
    gate = AnalogGate(duration=1 / 4, hamiltonian=[op], dissipation=[])
    ex = AnalogCircuit()
    ex.evolve(gate=gate)

    analog_args = TaskArgsAnalog(n_shots=10)
    analog_task = Task(program=ex, args=analog_args)

    ########################################################################################

    qreg = QuantumRegister(id="q", reg=2)
    creg = ClassicalRegister(id="c", reg=2)
    circ = DigitalCircuit(qreg=qreg, creg=creg)
    circ.add(H(qreg=qreg[0]))

    digital_args = TaskArgsDigital(repetitions=10)
    digital_task = Task(program=circ, args=digital_args)

    ########################################################################################

    g = globals().copy()

    for i in g.items():
        if isinstance(i[-1], BaseModel):
            serialization_test(*i, verbose=verbose)
