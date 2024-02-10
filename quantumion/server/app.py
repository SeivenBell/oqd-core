from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi import status as http_status

from rq.job import Callback
from rq.job import Job as RQJob

########################################################################################

from quantumion.backend.analog.python.qutip import QutipBackend
from quantumion.backend.digital.python.tc import TensorCircuitBackend
from quantumion.backend.task import Task

from quantumion.server.auth import user_dependency
from quantumion.server.database import (
    redis_client,
    queue,
    db_dependency,
    JobInDB,
    report_success,
    report_failure,
    report_stopped,
)
from quantumion.server.model import Job

from quantumion.server.auth import router as auth_router
from quantumion.server.user import router as user_router

########################################################################################

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)


@app.post("/submit/{backend}", tags=["Job"])
async def submit_job(
    task: Task,
    backend: Literal["qutip", "tensorcircuit"],
    user: user_dependency,
    db: db_dependency,
):
    print(f"Queueing {task} on server {backend} backend. {len(queue)} jobs in queue.")

    backends = {"qutip": QutipBackend(), "tensorcircuit": TensorCircuitBackend()}
    job = queue.enqueue(
        backends[backend].run,
        task,
        on_success=Callback(report_success),
        on_failure=Callback(report_failure),
        on_stopped=Callback(report_stopped),
    )

    job_in_db = JobInDB(
        job_id=job.id,
        task=task.model_dump_json(),
        backend=backend,
        status=job.get_status(),
        userid=user.userid,
        username=user.username,
        result=None,
    )
    db.add(job_in_db)
    db.commit()

    return Job.model_validate(job_in_db)


@app.get("/retrieve/{job_id}", tags=["Job"])
async def retrieve_job(job_id: str, user: user_dependency, db: db_dependency):
    job_in_db = (
        db.query(JobInDB)
        .filter(
            JobInDB.job_id == job_id,
            JobInDB.userid == user.userid,
            JobInDB.username == user.username,
        )
        .first()
    )
    if job_in_db:
        return Job.model_validate(job_in_db)

    raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED)


@app.delete("/cancel/{job_id}", tags=["Job"])
async def cancel_job(job_id: str, user: user_dependency, db: db_dependency):
    job_in_db = (
        db.query(JobInDB)
        .filter(
            JobInDB.job_id == job_id,
            JobInDB.userid == user.userid,
            JobInDB.username == user.username,
        )
        .first()
    )
    if job_in_db:
        job = RQJob.fetch(id=job_id, connection=redis_client)
        job.cancel()
        setattr(job_in_db, "status", "canceled")
        db.commit()
        return Job.model_validate(job_in_db)

    raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED)
