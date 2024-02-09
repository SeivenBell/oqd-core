import argparse

import numpy as np

########################################################################################

from quantumion.backend.client import Client
from quantumion.backend.provider import Provider

from quantumion.backend.task import Task, TaskArgsAnalog
from quantumion.interface.analog import *

########################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--url",
        default="http://10.104.2.129:8000",
        type=str,
        help="server URL for job submission",
    )

    args = parser.parse_args()

    url = args.url

    ########################################################################################

    provider = Provider(url)
    client = Client()

    client.connect(provider)

    ########################################################################################

    op = np.pi * PauliX @ PauliX
    gate = AnalogGate(duration=1 / 4, hamiltonian=[op], dissipation=[])
    ex = AnalogCircuit()
    ex.evolve(gate=gate)

    analog_args = TaskArgsAnalog(n_shots=10)
    analog_task = Task(program=ex, args=analog_args)

    ########################################################################################

    for i in range(10):
        client.submit_job(analog_task, backend="qutip")

    ########################################################################################

    while client.pending:
        print("\rJobs Pending ...", end="")
        client.status_update()

    print(client.jobs)

    ########################################################################################
