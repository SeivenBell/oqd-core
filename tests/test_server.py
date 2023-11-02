import requests
import numpy as np
import time

from quantumion.analog.experiment import Experiment
from quantumion.analog.gate import *
from backends.base import Submission, Specification

server_url = "http://localhost:8000"


def submit(submission: Submission):
    url = f"{server_url}/qsim_simulator/"
    response = requests.post(url, json=submission.model_dump())
    if response.status_code == 200:
        result = response.json()
        return result

    else:
        print(f"Error: {response.status_code}")
        return None


def get_result(result):
    url = f"{server_url}/get_result/"
    response = requests.post(url, json=result)
    if response.status_code == 200:
        result = response.json()
        return result

    else:
        print(f"Error: {response.status_code}")
        return None


if __name__ == "__main__":
    operator = np.pi * PauliX
    experiment = Experiment()
    experiment.add(operator)

    spec = Specification(n_shots=10, fock_trunc=4)
    submission = Submission(program=experiment, specification=spec)

    result = submit(submission)
    print(result)

    print("Just chillin, waiting for the queue to finish.")
    time.sleep(3)

    result = get_result(result)
    print(result)
