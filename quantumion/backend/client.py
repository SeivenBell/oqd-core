from typing import Literal

import requests

import numpy as np

from pydantic import TypeAdapter

########################################################################################

from quantumion.backend.provider import Provider
from quantumion.backend.task import Task, TaskResult
from quantumion.backend.job import Job

########################################################################################


class Client:
    def __init__(self):
        self._jobs = {}

    @property
    def jobs(self):
        return self._jobs

    @property
    def pending(self):
        return not np.array(
            [(job.status in ["failed", "finished"]) for job in self.jobs.values()]
        ).all()

    @property
    def provider(self):
        if hasattr(self, "_provider"):
            return self._provider
        raise ConnectionError("Missing provider")

    @property
    def token(self):
        if hasattr(self, "_token"):
            return self._token
        raise ConnectionError("Missing token")

    @property
    def authorization_header(self):
        return dict(
            Authorization="{} {}".format(
                self.token["token_type"], self.token["access_token"]
            )
        )

    def connect(self, provider: Provider):
        self._provider = provider

        username = input("Enter username: ")
        password = input("Enter password: ")
        login = dict(username=username, password=password)

        response = requests.post(
            provider.login_url,
            data=login,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code == 200:
            self._token = response.json()
            return

        raise response.raise_for_status()

    def reconnect(self):
        self.connect(self, self.provider)
        pass

    def submit_job(self, task: Task, backend: Literal["qutip", "tensorcircuit"]):

        response = requests.post(
            self.provider.job_submission_url(backend=backend),
            json=task.model_dump(),
            headers=self.authorization_header,
        )
        response_data = response.json()

        if response.status_code == 200:
            self._jobs[response_data["id"]] = Job(
                job_id=response_data["id"],
                task=task,
                status=response_data["status"],
                backend=backend,
            )
            return response_data["id"]

        raise response.raise_for_status()

    def retrieve_job(self, job_id):
        response = requests.get(
            self.provider.job_retrieval_url(job_id=job_id),
            headers=self.authorization_header,
        )
        response_data = response.json()

        if response.status_code == 200:
            self._jobs[job_id].status = response_data["status"]
            if self.jobs[job_id].status == "finished":
                self._jobs[job_id].result = TypeAdapter(TaskResult).validate_python(
                    response_data["result"]
                )

            return self.jobs[job_id]

        raise response.raise_for_status()

    def status_update(self):
        for job_id in self.jobs.keys():
            self.retrieve_job(job_id)
        pass

    def resubmit_job(self, job_id):
        return self.submit_job(
            self,
            task=self.jobs[job_id]["task"],
            backend=self.jobs[job_id]["backend"],
        )
