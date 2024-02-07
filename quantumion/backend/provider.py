import requests
from typing import Literal

########################################################################################

from quantumion.backend.task import Task

########################################################################################


class Provider:
    def __init__(self, url: str = "http://localhost:8000"):
        self.url = url

    def submit(self, task: Task, backend: Literal["qutip", "tensorcircuit"]):
        url = f"{self.url}/submit/{backend}"
        response = requests.post(url, json=task.model_dump())
        return response.json()

    def retrieve_job(self, job: dict):
        url = "{}/job/{}".format(self.url, job["id"])
        response = requests.get(url)
        return response.json()
