from utils.api import API
from config.const import BACKEND_URL


class DBModel:

    def __init__(self, name: str) -> None:
        self.name = name
        self.backend = API(base_url=BACKEND_URL)
        data = {"username": "worker", "password": "worker@123"}
        self.backend.post("auth/login/", data)
        csrf_token = self.backend.session.cookies.get("csrftoken")
        self.default_headers = {
            "X-CSRFToken": csrf_token,
        }

    def get(self, headers: dict = None, **kwargs) -> dict:
        headers = headers or {}
        headers = self.default_headers.copy()
        id = kwargs.get("id", None)
        if id is None:
            return self.backend.get(f"{self.name}/")
        try:
            response = self.backend.get(f"{self.name}/{id}/", headers=headers)
            return response
        except Exception as e:
            print(e, flush=True)
            return e

    def action(
        self,
        url: str = "",
        method: str = "GET",
        headers: dict = None,
        data: dict = None,
        **kwargs,
    ) -> dict:
        headers = headers or {}
        headers = self.default_headers.copy()
        id = kwargs.get("id", None)
        if id is None:
            return self.backend.request(
                method=method, url=f"{self.name}/{url}", headers=headers, data=data
            )
        try:
            response = self.backend.request(
                method=method, url=f"{self.name}/{id}/{url}", headers=headers, data=data
            )
            return response
        except Exception as e:
            print(e, flush=True)
            return str(e)

    def insert(self, data: dict, headers: dict = None) -> dict:
        headers = headers or {}
        headers.update(self.default_headers)
        try:
            response = self.backend.post(f"{self.name}/", data, headers=headers)
            return response
        except Exception as e:
            print(e, flush=True)
            return str(e)

    def update(self, id: str, data: dict, headers: dict = None) -> dict:
        headers = headers or {}
        headers.update(self.default_headers)
        try:
            response = self.backend.put(f"{self.name}/{id}/", data, headers=headers)
            return response
        except Exception as e:
            print(e, flush=True)
            return str(e)

    def delete(self, id: str, headers: dict = None) -> dict:
        headers = headers or {}
        headers.update(self.default_headers)
        try:
            response = self.backend.delete(f"{self.name}/{id}/", headers=headers)
            return response
        except Exception as e:
            print(e, flush=True)
            return str(e)


class DB:

    def model(self, name: str) -> DBModel:
        return DBModel(name)
