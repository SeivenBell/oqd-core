from pydantic import BaseModel
import requests
from typing import Union,Literal

from backends.task import (
    Task,
    TaskArgsAnalog,
    TaskResultAnalog,
    TaskArgsDigital,
    TaskResultDigital,
)


class Provider(BaseModel):
    url: str = "http://localhost:8000"

    def submit(self, task: Task, backend: Literal["qutip","tensorcircuit"]):
        url = f"{self.url}/submit/{backend}"
        response = requests.post(url, json=task.model_dump())
        return response.json()

    def retrieve_job(self, job: dict):
        url = "{}/job/{}".format(self.url, job["id"])
        response = requests.get(url)
        return response.json()
