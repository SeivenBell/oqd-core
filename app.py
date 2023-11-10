import os

from typing import Literal

from fastapi import FastAPI

from redis import Redis
from rq import Queue
from rq.job import Job

########################################################################################

from backends.analog.python.qutip import QutipBackend
from backends.digital.python.tc import TensorCircuitBackend
from backends.task import Task

########################################################################################

redis_client = Redis(host=os.environ["REDIS_HOST"], port=6379, decode_responses=False)
queue = Queue(connection=redis_client)

########################################################################################

app = FastAPI()


@app.post("/submit/{backend}")
async def submit(submission: Task, backend: Literal["qutip","tensorcircuit"]):
    backends = {"qutip":QutipBackend, "tensorcircuit":TensorCircuitBackend}

    print(f"Queueing {submission} on server {backend} backend. {len(queue)} jobs in queue.")

    job = queue.enqueue(backends[backend]().run, submission)
    return {"id": job.id, "status": job.get_status()}


@app.get("/job/{job_id}")
async def retrieve_job(job_id: str):
    print(f"Requesting status of job {job_id}")
    job = Job.fetch(id=job_id, connection=redis_client)

    status = job.get_status()
    if status != "finished":
        return {"id": job_id, "status": status}

    result = job.return_value()

    return {"id": job_id, "status": status, "result": result}
