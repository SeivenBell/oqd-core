import requests
import numpy as np
import time

from quantumion.analog.circuit import AnalogCircuit
from quantumion.analog.gate import *
from backends.task import Task
from backends.base import TaskArgs

server_url = "http://localhost:8000"


def submit(submission: Task):
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
    experiment = AnalogCircuit()
    experiment.add(operator)

    spec = TaskArgs(n_shots=10, fock_trunc=4)
    submission = Task(program=experiment, specification=spec)

    result = submit(submission)
    print(result)

    print("Just chillin, waiting for the queue to finish.")
    time.sleep(3)

    result = get_result(result)
    print(result)
