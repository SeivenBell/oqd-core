import argparse

import requests

########################################################################################

from fastapi.security import OAuth2PasswordRequestForm

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

    login = dict(username=username, password=password)

    login_url = BASE_URL + "/auth/token/"
    response = requests.post(
        login_url,
        data=login,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    print(response.__dict__)
