from backend import Backend


class DBModel:

    def __init__(self, name: str) -> None:
        self.name = name
        self.backend = Backend()

    def get(self, **kwargs) -> dict:
        id = kwargs.get("id", None)
        if id is None:
            return self.backend.get(f"{self.name}/")
        return self.backend.get(f"{self.name}/{id}/")

    def insert(self, data: dict) -> dict:
        return self.backend.post(f"{self.name}/", data)

    def update(self, id: str, data: dict) -> dict:
        return self.backend.put(f"{self.name}/{id}/", data)

    def delete(self, id: str) -> dict:
        return self.backend.delete(f"{self.name}/{id}/")


class DB:

    def model(self, name: str) -> DBModel:
        return DBModel(name)
