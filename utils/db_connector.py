import psycopg2


class DBWrapper:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()


class DBConnector:
    def connect(self, dbname, user, password, host, port) -> DBWrapper:
        connector = DBWrapper(dbname, user, password, host, port)
        connector.connect()
        return connector
