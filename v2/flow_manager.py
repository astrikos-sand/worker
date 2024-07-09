from concurrent.futures import ThreadPoolExecutor
from v2.mappings import FLOW_STATUS
from v2.node_manager import NodeManager
from threading import Lock


class FlowManager:
    def __init__(self, flow: dict, nodes: list, inputs: dict):
        self.nodes = nodes
        self.inputs = inputs
        self.flow = flow

        self.outputs = {}
        self.start_nodes = []
        self.nodes_dict = {}
        self.lock = Lock()
        self.status = FLOW_STATUS.PENDING.value

    # Filter start nodes
    def filter_start_nodes(self):
        for node in self.nodes:
            id = node.get("id", None)
            self.nodes_dict.update({id: node})
            slots = node.get("input_slots", [])

            if len(slots) == 0:
                self.start_nodes.append(id)

    # Manager that manages a node and its children
    def node_and_children_manager(self, node_id: str):
        node = self.nodes_dict.get(node_id)
        node_manager = NodeManager(node, self.nodes_dict, self.lock)
        node_manager.manage()

        children = node_manager.children

        for child_id in children:
            self.node_and_children_manager(child_id)

    # Execute the flow
    def manage(self):
        self.filter_start_nodes()

        with ThreadPoolExecutor(10) as executor:
            for node_id in self.start_nodes:
                executor.submit(self.node_and_children_manager, node_id)
