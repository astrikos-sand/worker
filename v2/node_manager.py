from threading import Lock
from v2.node import BaseNode


class NodeManager:
    executors = {}

    @classmethod
    def register(cls, node_type: str, executor):
        cls.executors[node_type] = executor

    def __init__(
        self,
        node: BaseNode,
        nodes_dict: dict[str, BaseNode],
        lock: Lock,
        inputs: dict,
        outputs: dict,
        **kwargs
    ) -> None:
        self.node = node
        self.lock = lock
        self.nodes_dict = nodes_dict
        self.children = []
        self.flow_inputs = inputs
        self.flow_outputs = outputs
        self.kwargs = kwargs

    @property
    def executor(self):
        return self.executors.get(self.node.node_type)

    def manage(self):
        node_executor = self.executor(
            self.node,
            self.node.inputs,
            self.lock,
            self.nodes_dict,
            flow_inputs=self.flow_inputs,
            flow_outputs=self.flow_outputs,
            global_dict=self.kwargs.get("global_dict"),
        )
        node_executor.manage()
        self.children = node_executor.children
