from api import API
from const import BACKEND_URL
import json


class DBModel:

    def __init__(self, name: str) -> None:
        self.name = name
        self.backend = API(base_url=BACKEND_URL)
        data = {
            'username': 'worker',
            'password': 'worker@123'
        }
        self.backend.post("auth/login/", data)
        csrf_token = self.backend.session.cookies.get('csrftoken')
        self.default_headers = {
            'X-CSRFToken': csrf_token,
        }
        print(f'cookies: {self.backend.session.cookies.get_dict()}')

    def get(self, headers: dict=None, **kwargs) -> dict:
        headers = headers or {}
        headers = self.default_headers.copy()
        id = kwargs.get("id", None)
        if id is None:
            return self.backend.get(f"{self.name}/")
        return self.backend.get(f"{self.name}/{id}/", headers=headers)

    def insert(self, data: dict, headers: dict=None) -> dict:
        headers = headers or {}
        headers.update(self.default_headers)
        return self.backend.post(f"{self.name}/", data,headers=headers)

    def update(self, id: str, data: dict, headers: dict=None) -> dict:
        headers = headers or {}
        headers.update(self.default_headers)
        return self.backend.put(f"{self.name}/{id}/", data, headers=headers)

    def delete(self, id: str, headers: dict=None) -> dict:
        headers = headers or {}
        headers.update(self.default_headers)
        return self.backend.delete(f"{self.name}/{id}/",headers=headers)


class DB:

    def model(self, name: str) -> DBModel:
        return DBModel(name)
