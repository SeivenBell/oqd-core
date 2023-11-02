import os

from fastapi import FastAPI

from redis import Redis
from rq import Queue
from rq.job import Job

########################################################################################

from backends.qsim.qutip import QutipBackend
from backends.task import Task, TaskArgs, TaskResult

########################################################################################

app = FastAPI()
redis = Redis()

try:
    r = Redis(host=os.environ["REDIS_HOST"], port=6379, decode_responses=True)
except:
    r = Redis(host="localhost", port=6379, decode_responses=True)
queue = Queue(connection=redis)


@app.post("/qsim_simulator/")
async def submit(submission: Task):
    print(f"Queueing {submission} on server backend. {len(queue)} jobs in queue.")
    j = queue.enqueue(run, submission)
    return {"id": j.id, "status": j.get_status()}


def run(submission):
    print(f"Now running {submission}")
    backend = QutipBackend()
    result = backend.run(submission)
    return result


@app.post("/check_status/")
async def check_status(request: dict):
    print(f"Requesting status of job {request['id']}")
    job = Job.fetch(id=request["id"], connection=redis)
    return {"id": job.id, "status": job.get_status()}


@app.post("/get_result/")
async def get_result(request: dict):
    print(f"Requesting result for job {request['id']}")
    job = Job.fetch(id=request["id"], connection=redis)
    print(job.get_status())
    return job.return_value()


########################################################################################

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
