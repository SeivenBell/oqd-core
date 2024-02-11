from fastapi import FastAPI

from quantumion.server.route import user_router, auth_router, job_router

########################################################################################

app = FastAPI()
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(job_router)
