import os

from typing import Literal

from fastapi import FastAPI, HTTPException, status

from redis import Redis
from rq import Queue
from rq.job import Job

########################################################################################

from quantumion.backend.analog.python.qutip import QutipBackend
from quantumion.backend.digital.python.tc import TensorCircuitBackend
from quantumion.backend.task import Task

from quantumion.server import auth
from quantumion.server.auth import user_dependency

########################################################################################

redis_client = Redis(host=os.environ["REDIS_HOST"], port=6379, decode_responses=False)
queue = Queue(connection=redis_client)

########################################################################################

app = FastAPI()
app.include_router(auth.router)


@app.post("/submit/{backend}", tags=["job"])
async def submit_job(
    task: Task, backend: Literal["qutip", "tensorcircuit"], user: user_dependency
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    backends = {"qutip": QutipBackend(), "tensorcircuit": TensorCircuitBackend()}

    print(f"Queueing {task} on server {backend} backend. {len(queue)} jobs in queue.")

    job = queue.enqueue(backends[backend].run, task)
    return {"id": job.id, "status": job.get_status()}


@app.get("/job/{job_id}", tags=["job"])
async def retrieve_job(job_id: str, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    print(f"Requesting status of job {job_id}")
    job = Job.fetch(id=job_id, connection=redis_client)

    status = job.get_status()
    if status != "finished":
        return {"id": job_id, "status": status}

    result = job.return_value()

    return {"id": job_id, "status": status, "result": result}
