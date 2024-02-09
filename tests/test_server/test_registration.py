import argparse

import requests

########################################################################################

from quantumion.server.model import UserRegistrationForm

########################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--url",
        default="http://10.104.2.129:8000",
        type=str,
        help="server URL for job submission",
    )

    args = parser.parse_args()

    BASE_URL = args.url

    username = "test_user"
    password = "test_password"

    registration = UserRegistrationForm(username=username, password=password)

    registration_url = BASE_URL + "/auth/register"
    response = requests.post(registration_url, json=registration.model_dump())
