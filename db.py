from api import API
from const import BACKEND_URL


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

    def get(self, headers: dict=None, **kwargs) -> dict:
        headers = headers or {}
        headers = self.default_headers.copy()
        id = kwargs.get("id", None)
        if id is None:
            return self.backend.get(f"{self.name}/")
        try:
            response = self.backend.get(f"{self.name}/{id}/", headers=headers)
            response.raise_for_status()
            return response
        except Exception as e:
            print(e, flush=True)
            return response

    def insert(self, data: dict, headers: dict=None) -> dict:
        headers = headers or {}
        headers.update(self.default_headers)
        try:
            response = self.backend.post(f"{self.name}/", data,headers=headers)
            response.raise_for_status()
            return response
        except Exception as e:
            print(e, flush=True)
            return response


    def update(self, id: str, data: dict, headers: dict=None) -> dict:
        headers = headers or {}
        headers.update(self.default_headers)
        try:
            response = self.backend.put(f"{self.name}/{id}/", data, headers=headers)
            response.raise_for_status()
            return response
        except Exception as e:
            print(e, flush=True)
            return response 

    def delete(self, id: str, headers: dict=None) -> dict:
        headers = headers or {}
        headers.update(self.default_headers)
        try:
            response = self.backend.delete(f"{self.name}/{id}/",headers=headers)
            response.raise_for_status()
            return response
        except Exception as e:
            print(e, flush=True)
            return response


class DB:

    def model(self, name: str) -> DBModel:
        return DBModel(name)
