import pyodbc


class MssqlConnector:
    def __init__(
        self,
        server: str,
        database: str,
        username: str,
        password: str,
        driver: str,
    ):
        self.conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        self.connection = None

    def connect(self):
        self.connection = pyodbc.connect(self.conn_str)

    def close(self):
        self.connection.close()
