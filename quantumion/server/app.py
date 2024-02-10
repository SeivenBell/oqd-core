import os

from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi import status as http_status

from redis import Redis
from rq import Queue
from rq.job import Job

########################################################################################

from quantumion.backend.analog.python.qutip import QutipBackend
from quantumion.backend.digital.python.tc import TensorCircuitBackend
from quantumion.backend.task import Task

from quantumion.server import auth
from quantumion.server.auth import user_dependency, db_dependency
from quantumion.server.database import JobInDB

########################################################################################

redis_client = Redis(host=os.environ["REDIS_HOST"], port=6379, decode_responses=False)
queue = Queue(connection=redis_client)

########################################################################################

app = FastAPI()
app.include_router(auth.router)


@app.post("/submit/{backend}", tags=["job"])
async def submit_job(
    task: Task,
    backend: Literal["qutip", "tensorcircuit"],
    user: user_dependency,
    db: db_dependency,
):
    print(f"Queueing {task} on server {backend} backend. {len(queue)} jobs in queue.")

    backends = {"qutip": QutipBackend(), "tensorcircuit": TensorCircuitBackend()}
    job = queue.enqueue(backends[backend].run, task)

    job_in_db = JobInDB(jobid=job.id, userid=user.userid, username=user.username)
    db.add(job_in_db)
    db.commit()

    return {"id": job.id, "status": job.get_status()}


@app.get("/retrieve/{job_id}", tags=["job"])
async def retrieve_job(job_id: str, user: user_dependency, db: db_dependency):
    job_in_db = (
        db.query(JobInDB)
        .filter(
            JobInDB.jobid == job_id,
            JobInDB.userid == user.userid,
            JobInDB.username == user.username,
        )
        .first()
    )
    if job_in_db:
        job = Job.fetch(id=job_id, connection=redis_client)
        status = job.get_status()
        result = job.return_value()
        return {"id": job_id, "status": status, "result": result}

    raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED)


@app.delete("/cancel/{job_id}", tags=["job"])
async def cancel_job(job_id: str, user: user_dependency, db: db_dependency):
    job_in_db = (
        db.query(JobInDB)
        .filter(
            JobInDB.jobid == job_id,
            JobInDB.userid == user.userid,
            JobInDB.username == user.username,
        )
        .first()
    )
    if job_in_db:
        job = Job.fetch(id=job_id, connection=redis_client)
        job.cancel()
        status = job.get_status()
        result = job.return_value()
        return {"id": job_id, "status": status, "result": result}

    raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED)
