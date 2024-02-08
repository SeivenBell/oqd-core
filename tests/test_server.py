import numpy as np

import argparse

########################################################################################

from quantumion.backend.task import Task, TaskArgsAnalog, TaskArgsDigital
from quantumion.backend.provider import Provider

from quantumion.interfaces.analog import *
from quantumion.interfaces.digital import *

########################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--url",
        default="http://127.0.0.1:8000",
        type=str,
        help="server URL for job submission",
    )
    parser.add_argument(
        "-N",
        default=1,
        type=int,
        help="Number of repetitions",
    )
    parser.add_argument(
        "-B",
        default=1,
        type=int,
        help="Number of samples per repetition",
    )

    args = parser.parse_args()
    URL = args.url
    N = args.N
    B = args.B

    ########################################################################################

    client = Provider(url=URL)

    ########################################################################################

    print("{:=^80}".format(" Submitting Jobs "))

    n = 0
    jobs = []

    ########################################################################################

    op = np.pi * PauliX @ PauliX
    gate = AnalogGate(duration=1 / 4, hamiltonian=[op], dissipation=[])
    ex = AnalogCircuit()
    ex.evolve(gate=gate)

    analog_args = TaskArgsAnalog(n_shots=B)
    analog_task = Task(program=ex, args=analog_args)
    for _ in range(N):
        job = client.submit(analog_task, backend="qutip")
        job_id = job["id"]
        jobs.append(job)
        print(f"Job {n} submitted with ID: {job_id}")
        n += 1

    ########################################################################################

    qreg = QuantumRegister(id="q", reg=2)
    creg = ClassicalRegister(id="c", reg=2)
    circ = DigitalCircuit(qreg=qreg, creg=creg)
    circ.add(H(qreg=qreg[0]))
    circ.add(CNOT(qreg=qreg[0:2]))

    digital_args = TaskArgsDigital(repetitions=B)
    digital_task = Task(program=circ, args=digital_args)

    for _ in range(N):
        job = client.submit(digital_task, backend="tensorcircuit")
        job_id = job["id"]
        jobs.append(job)
        print(f"Job {n} submitted with ID: {job_id}")
        n += 1

    #######################################################################################

    print("{:=^80}".format(" Results "))

    print("{:<5} {:<12} {}".format("Job", "Status", "Result"))

    for n, job in enumerate(jobs):
        status = ""
        while status not in ["finished", "failed"]:
            job = client.retrieve_job(job)
            status = job["status"]

            if status == "finished":
                print("\r{:<5} {:<12} {}".format(n, status, job["result"]))
            elif status == "failed":
                print("\r{:<5} {:<12} {}".format(n, status, ""))
            else:
                print("\r{:<5} {:<12} {}".format(n, status, ""), end="")
