from config.const import TB_BACKEND_URL
import requests
from requests.models import Response


class TBModel:

    def __init__(self) -> None:
        data = {"username": "tenant@thingsboard.org", "password": "tenant"}
        response = requests.post(f"{TB_BACKEND_URL}/api/auth/login", json=data)
        token = response.json().get("token")
        self.default_headers = {
            "X-Authorization": f"Bearer {token}",
        }

    def backend(self, url: str, method: str, data: dict, headers: dict) -> Response:
        if headers is None:
            headers = self.default_headers
        return getattr(requests, method)(
            f"{TB_BACKEND_URL}{url}", json=data, headers=headers
        )


class TB:

    def model(
        self, url: str, method: str = "get", data: dict = None, headers: dict = None
    ) -> Response:
        return TBModel().backend(url, method, data, headers)
