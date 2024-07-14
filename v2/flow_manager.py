from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import copy

from v2.mappings import FLOW_STATUS
from v2.node_manager import NodeManager
from v2.node import BaseNode


class FlowManager:
    def __init__(self, flow: dict, nodes: list, inputs: dict = {}):
        self.nodes = copy.deepcopy(nodes)
        self.inputs = copy.deepcopy(inputs)
        self.flow = copy.deepcopy(flow)

        self.outputs = {}
        self.start_nodes = []
        self.nodes_dict: dict[str, BaseNode] = {}
        self.lock = Lock()
        self.status = FLOW_STATUS.PENDING.value
        self.futures = []

    # Filter start nodes
    def filter_start_nodes(self):
        for node in self.nodes:
            node_obj = BaseNode(node)

            self.nodes_dict.update({node_obj.id: node_obj})
            slots = node_obj.input_slots

            if len(slots) == 0:
                self.start_nodes.append(node_obj.id)

    # Manager that manages a node and its children
    def node_and_children_manager(self, node_id: str):
        node = self.nodes_dict.get(node_id)

        node_manager = NodeManager(
            node, self.nodes_dict, self.lock, self.inputs, self.outputs
        )
        node_manager.manage()

        children = node_manager.children

        with ThreadPoolExecutor(5) as executor:
            for child_id in children:
                future = executor.submit(self.node_and_children_manager, child_id)
                self.futures.append(future)

    # Execute the flow
    def manage(self):
        self.filter_start_nodes()

        with ThreadPoolExecutor(5) as executor:
            for node_id in self.start_nodes:
                future = executor.submit(self.node_and_children_manager, node_id)
                self.futures.append(future)

    def wait_for_completion(self):
        for future in self.futures:
            future.result()
