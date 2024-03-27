import requests

from constants import BACKEND_URL


class Backend:

    def __init__(self):
        self.backend_url = BACKEND_URL

    def get(self, url: str) -> str:
        try:
            response = requests.get(f"{self.backend_url}{url}")
            if response.status_code < 200 and response.status_code >= 300:
                raise Exception(f"error: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching from backend: {str(e)}")

    def post(self, url: str, data: dict) -> str:
        try:
            response = requests.post(f"{self.backend_url}{url}", json=data)
            if response.status_code < 200 and response.status_code >= 300:
                raise Exception(f"error: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            print(f"Error making post request to backend: {str(e)}")

    def put(self, url: str, data: dict) -> str:
        try:
            response = requests.patch(f"{self.backend_url}{url}", json=data)
            if response.status_code < 200 and response.status_code >= 300:
                raise Exception(f"error: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            print(f"Error making put request to backend: {str(e)}")

    def delete(self, url: str) -> str:
        try:
            response = requests.delete(f"{self.backend_url}{url}")
            if response.status_code < 200 and response.status_code >= 300:
                raise Exception(f"error: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            print(f"Error making delete request to backend: {str(e)}")
