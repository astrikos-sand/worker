import pika
from config.const import TBQ_HOST


class QueueProducer:
    def __init__(self) -> None:
        credentials = pika.PlainCredentials("root", "root")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=TBQ_HOST, credentials=credentials, port="5672", virtual_host="/"
            )
        )
        self.channel = connection.channel()

    def publish(self, body, routing_key):
        self.channel.basic_publish(body=body, exchange="", routing_key=routing_key)


class TBQueue:
    def producer(self):
        return QueueProducer()
