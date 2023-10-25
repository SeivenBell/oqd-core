from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import requests
from tests.pyd import Experiment, Operator, PauliX, PauliY, PauliZ, PauliI


# Define the server URL
server_url = "http://localhost:8000"  # Adjust the URL as needed


def submit_job(experiment: Experiment):
    url = f"{server_url}/qsim_simulator/"
    response = requests.post(url, json=experiment.model_dump())

    if response.status_code == 200:
        result = response.json()
        return result

    else:
        print(f"Error: {response.status_code}")
        return None


if __name__ == "__main__":

    operator = PauliX + PauliI
    experiment = Experiment(sequence=[operator])
    result = submit_job(experiment)

    if result:
        print(f"Job id: {result['id']}Result: {result['result']}")
