from strenum import StrEnum

from wrappers.db_connector.postgres import PostgresConnector
from wrappers.db_connector.mssql import MssqlConnector
from wrappers.db_connector.mongo import MongoDBConnector


class CONNECTORS(StrEnum):
    POSTGRES = "postgres"
    MONGODB = "mongodb"
    MSSQL = "mssql"


class DBConnector:
    def __init__(self, type: str) -> None:
        self.type = CONNECTORS(type.lower())
        self.set_connector()

    def set_connector(self) -> None:
        match self.type:
            case CONNECTORS.POSTGRES:
                self.connector = self.postgres_connector
            case CONNECTORS.MONGODB:
                self.connector = self.mongo_connector
            case CONNECTORS.MSSQL:
                self.connector = self.mssql_connector

    def set_config(self, *args, **kwargs):
        return self.connector(*args, **kwargs)

    def postgres_connector(
        self, dbname, user, password, host, port
    ) -> PostgresConnector:
        connector = PostgresConnector(dbname, user, password, host, port)
        return connector

    def mssql_connector(
        self, server, database, username, password, driver
    ) -> MssqlConnector:
        connector = MssqlConnector(server, database, username, password, driver)
        return connector

    def mongo_connector(self, uri, dbname) -> MongoDBConnector:
        connector = MongoDBConnector(uri, dbname)
        return connector
