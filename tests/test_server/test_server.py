import numpy as np

import argparse

import requests

########################################################################################

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

    BASE_URL = args.url

    ########################################################################################

    username = "test_user"
    password = "test_password"

    login = dict(username=username, password=password)

    login_url = BASE_URL + "/auth/token/"
    token = requests.post(
        login_url,
        data=login,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()

    ########################################################################################

    op = np.pi * PauliX @ PauliX
    gate = AnalogGate(duration=1 / 4, hamiltonian=[op], dissipation=[])
    ex = AnalogCircuit()
    ex.evolve(gate=gate)

    analog_args = TaskArgsAnalog(n_shots=100)
    analog_task = Task(program=ex, args=analog_args)

    ########################################################################################

    submission_url = BASE_URL + "/submit/{}".format("qutip")
    job = requests.post(
        submission_url,
        json=analog_task.model_dump(),
        headers={
            "Authorization": "{} {}".format(token["token_type"], token["access_token"]),
        },
    ).json()

    ########################################################################################

    retrieval_url = BASE_URL + "/job/{}".format(job["id"])

    status = job["status"]
    while status not in ["finished", "failed"]:
        job = requests.get(
            retrieval_url,
            headers={
                "Authorization": "{} {}".format(
                    token["token_type"], token["access_token"]
                ),
            },
        ).json()
        status = job["status"]

        if status == "finished":
            print("\r{:<40} {:<12} {}".format(job["id"], status, job["result"]))
        elif status == "failed":
            print("\r{:<40} {:<12} {}".format(job["id"], status, ""))
        else:
            print("\r{:<40} {:<12} {}".format(job["id"], status, ""), end="")
