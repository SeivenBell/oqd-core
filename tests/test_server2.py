import time

import requests

import numpy as np

import argparse

########################################################################################

from quantumion.hamiltonian.experiment import Experiment
from quantumion.hamiltonian.operator import *

from backends.base import Submission, Specification, run

########################################################################################


def submit(submission: Submission):
    url = f"{server_url}/qsim_simulator/"
    response = requests.post(url, json=submission.model_dump())
    if response.status_code == 200:
        result = response.json()
        return result

    else:
        print(f"Error: {response.status_code}")
        return None


def check_status(result):
    url = f"{server_url}/check_status/"
    response = requests.post(url, json=result)
    if response.status_code == 200:
        result = response.json()
        return result


def get_result(result):
    url = f"{server_url}/get_result/"
    response = requests.post(url, json=result)
    if response.status_code == 200:
        result = response.json()
        return result

    else:
        print(f"Error: {response.status_code}")
        return None


########################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", default="http://127.0.0.1:8000", type=str, help="server URL for job submission")

    args = parser.parse_args()

    server_url = args.url

    operator = 0.25 * np.pi * PauliX @ PauliX
    experiment = Experiment()
    experiment.add(operator)

    spec = Specification(n_shots=10, fock_trunc=4)
    submission = Submission(program=experiment, specification=spec)

    print("{:=^80}".format(" Submitting Jobs "))

    jobs = []
    for n in range(10):
        job = submit(submission)
        job_id = job["id"]
        jobs.append(job)
        print(f"Job {n} submitted with ID: {job_id}")

    print("{:=^80}".format(" Results "))

    print("{:<5} {:<12} {}".format("Job", "Status", "Result"))

    for n, job in enumerate(jobs):
        status = ""
        while status != "finished":
            status = check_status(job)["status"]

            if status != "finished":
                print("\r{:<5} {:<12} {}".format(n, status, ""), end="")
            else:
                result = get_result(job)
                print("\r{:<5} {:<12} {}".format(n, status, result))
