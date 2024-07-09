from pymongo import MongoClient


class MongoDBConnector:
    def __init__(self, uri: str, dbname: str):
        self.uri = uri
        self.dbname = dbname
        self.client = None
        self.db = None

    def connect(self):
        self.client = MongoClient(self.uri)
        self.db = self.client[self.dbname]

    def disconnect(self):
        self.client.close()
