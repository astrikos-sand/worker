from threading import Lock
from v2.node import BaseNode


class NodeManager:
    executors = {}

    @classmethod
    def register(cls, node_type: str, executor):
        cls.executors[node_type] = executor

    def __init__(
        self, node: BaseNode, nodes_dict: dict[str, BaseNode], lock: Lock
    ) -> None:
        self.node = node
        self.lock = lock
        self.nodes_dict = nodes_dict
        self.children = []

    @property
    def executor(self):
        return self.executors.get(self.node.node_type)

    def is_ready_for_execution(self) -> bool:
        for connection in self.node.connections_in:
            source_id = connection.get("source")
            source = self.nodes_dict.get(source_id)

            if not source.executed:
                return False

        return True

    def manage(self):
        if self.is_ready_for_execution():
            if not all(
                param in self.node.inputs
                for param in self.node.input_slots_names.keys()
            ):
                raise Exception(
                    f"All inputs are not available for node {self.node.id}, available inputs {self.node.inputs}, required inputs {self.node.input_slots_names.keys()}"
                )

            node_executor = self.executor(
                self.node, self.node.inputs, self.lock, self.nodes_dict
            )
            node_executor.manage()
            self.children = node_executor.children

            with self.lock:
                self.nodes_dict.get(self.node.id).executed = True