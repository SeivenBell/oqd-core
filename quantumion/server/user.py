from fastapi import APIRouter, HTTPException
from fastapi import status as http_status

from rq.job import Job

########################################################################################

from quantumion.server.auth import user_dependency, db_dependency, pwd_context

from quantumion.server.model import UserRegistrationForm

from quantumion.server.database import redis_client, UserInDB, JobInDB

########################################################################################

router = APIRouter(prefix="/user", tags=["user"])

########################################################################################


def available_user(user, db):
    user_in_db = db.query(UserInDB).filter(UserInDB.username == user.username).first()
    if not user_in_db:
        return user

    raise HTTPException(status_code=http_status.HTTP_409_CONFLICT)


########################################################################################


@router.post(
    "/register",
    status_code=http_status.HTTP_201_CREATED,
)
async def register_user(create_user_form: UserRegistrationForm, db: db_dependency):
    user = available_user(create_user_form, db)
    if user:
        user_in_db = UserInDB(
            username=user.username,
            hashed_password=pwd_context.hash(user.password),
        )

        db.add(user_in_db)
        db.commit()
    pass


@router.get("/jobs", tags=["user", "job"])
async def user_jobs(user: user_dependency, db: db_dependency):
    jobs_in_db = (
        db.query(JobInDB)
        .filter(
            JobInDB.userid == user.userid,
            JobInDB.username == user.username,
        )
        .all()
    )
    if jobs_in_db:
        job_ids = {job_in_db.jobid for job_in_db in jobs_in_db}

        jobs = []
        for job_id in job_ids.copy():
            try:
                jobs.append(Job.fetch(id=job_id, connection=redis_client).get_status())
            except:
                job_ids.remove(job_id)
        return job_ids

    raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED)
