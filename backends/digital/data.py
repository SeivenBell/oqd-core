from pydantic import BaseModel


class TaskArgsDigital(BaseModel):
    n_shots: int = 10


class TaskResultDigital(BaseModel):
    counts: dict[int, int] = {}
