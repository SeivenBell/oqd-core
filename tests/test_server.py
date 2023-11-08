import time

import requests

import numpy as np

import argparse

########################################################################################

from backends.task import Task, TaskArgsAnalog
from backends.provider import Provider

from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.gate import *
from quantumion.analog.operator import *

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

    args = parser.parse_args()
    server_url = args.url
    client = Provider(url=server_url)

    ########################################################################################
    op = np.pi * PauliX
    gate = AnalogGate(duration=1 / 4, unitary=[op], dissipation=[])
    ex = AnalogCircuit()
    ex.add(gate=gate)

    spec = TaskArgsAnalog(n_shots=10)
    submission = Task(program=ex, args=spec)

    print("{:=^80}".format(" Submitting Jobs "))

    jobs = []
    for n in range(10):
        job = client.submit(submission)
        job_id = job["id"]
        jobs.append(job)
        print(f"Job {n} submitted with ID: {job_id}")

    ########################################################################################

    print("{:=^80}".format(" Results "))

    print("{:<5} {:<12} {}".format("Job", "Status", "Result"))

    for n, job in enumerate(jobs):
        status = ""
        while status not in ["finished", "failed"]:
            status = client.check_status(job)["status"]

            if status == "finished":
                result = client.get_result(job)
                print("\r{:<5} {:<12} {}".format(n, status, result))
            elif status == "failed":
                result = client.get_result(job)
                print("\r{:<5} {:<12} {}".format(n, status, ""))
            else:
                print("\r{:<5} {:<12} {}".format(n, status, ""), end="")
