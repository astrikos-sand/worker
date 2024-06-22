import requests


class API:

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def request(
        self, method: str, url: str, data: dict = None, headers: dict = None
    ) -> str:
        try:
            response = self.session.request(
                method=method, url=f"{self.base_url}{url}", headers=headers, json=data
            )
            response.reason = response.json()
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching from backend: {str(e)}")
            return str(e)

    def get(self, url: str, headers: dict = None) -> str:
        try:
            response = self.session.get(f"{self.base_url}{url}", headers=headers)
            response.reason = response.json()
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching from backend: {str(e)}")
            return str(e)

    def post(self, url: str, data: dict, headers: dict = None, files=None) -> str:
        try:
            response = self.session.post(
                f"{self.base_url}{url}", json=data, headers=headers, files=files
            )
            response.reason = response.json()
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error making post request to backend: {str(e)}")
            return str(e)

    def put(self, url: str, data: dict, headers: dict = None) -> str:
        try:
            response = self.session.patch(
                f"{self.base_url}{url}", json=data, headers=headers
            )
            response.reason = response.json()
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error making put request to backend: {str(e)}")
            return str(e)

    def delete(self, url: str, headers: dict = None) -> str:
        try:
            response = self.session.delete(f"{self.base_url}{url}", headers=headers)
            response.reason = response.json()
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error making delete request to backend: {str(e)}")
            return str(e)
