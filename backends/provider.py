from pydantic import BaseModel
import requests
from typing import Union

from backends.task import (
    Task,
    TaskArgsAnalog,
    TaskResultAnalog,
    TaskArgsDigital,
    TaskResultDigital,
)


class Provider(BaseModel):
    url: str = "http://localhost:8000"

    def submit(self, task: Task):
        url = f"{self.url}/submit/"
        response = requests.post(url, json=task.model_dump())
        return response.json()

    def retrieve_job(self, job: dict):
        url = "{}/job/{}".format(self.url, job["id"])
        response = requests.get(url)
        return response.json()
