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
        url = f"{self.url}/qsim_simulator/"
        response = requests.post(url, json=task.model_dump())
        return response.json()

    def get_result(self, job: dict):
        url = f"{self.url}/get_result/"
        response = requests.post(url, json=job)
        return response.json()

    def check_status(self, job: dict) -> Union[TaskResultDigital, TaskResultAnalog]:
        url = f"{self.url}/check_status/"
        response = requests.post(url, json=job)
        return response.json()
