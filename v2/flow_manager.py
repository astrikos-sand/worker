from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import copy
from datetime import datetime

from v2.mappings import FLOW_STATUS
from v2.node_manager import NodeManager
from v2.node import BaseNode
from config.const import BACKEND_URL, BASE_DIR


class FlowManager:
    def __init__(self, flow: dict, nodes: list, inputs: dict = {}, **kwargs):
        self.nodes = copy.deepcopy(nodes)
        self.inputs = copy.deepcopy(inputs)
        self.flow = copy.deepcopy(flow)
        self.execution_id: str = kwargs.get("execution_id", None)

        self.outputs = {}
        self.start_nodes = []
        self.nodes_dict: dict[str, BaseNode] = {}
        self.lock = Lock()
        self.status = FLOW_STATUS.PENDING.value
        self.futures = []
        self.global_dict = {"globals": {}, "lock": Lock()}

        self.set_flow_name()

        self.logs: dict[str, dict] = {
            "flow": {
                "id": self.flow.get("id"),
                "name": self.flow_name,
                "logs": [],
            },
            "nodes": {},
            "timestamp": {},
        }

    def set_flow_name(self):
        self.flow_name = self.flow.get("name")

        # if self.flow.get("prefix") is not None:
        #     self.flow_name = (
        #         f"{self.flow.get('prefix').get('full_name')}/{self.flow.get('name')}"
        #     )

    def node_logger(
        self,
        node_id: str,
        message,
        timestamp: str | None = None,
        error: bool = False,
    ):
        try:
            message_str = str(message)
        except Exception as e:
            message_str = f"Error in converting message to string: {e}"
            error = True

        if timestamp is None:
            timestamp = datetime.now().strftime("%M:%S")

        self.logs["timestamp"].setdefault(timestamp, [])

        self.logs["timestamp"][timestamp].append(
            {
                "node_id": node_id[:7],
                "message": message_str,
                "node_type": self.nodes_dict.get(node_id).node_type,
                **self.nodes_dict.get(node_id).details,
                "error": error,
            }
        )

        self.logs["nodes"].setdefault(
            node_id,
            {
                "logs": [],
                "node_type": self.nodes_dict.get(node_id).node_type,
                **self.nodes_dict.get(node_id).details,
            },
        )

        self.logs["nodes"][node_id]["logs"].append(
            {"message": message_str, "timestamp": timestamp, "error": error}
        )

    def flow_logger(self, message, timestamp: str | None = None, error: bool = False):
        try:
            message_str = str(message)
        except Exception as e:
            message_str = f"Error in converting message to string: {e}"
            error = True

        if timestamp is None:
            timestamp = datetime.now().strftime("%M:%S")

        self.logs["timestamp"].setdefault(timestamp, [])

        self.logs["timestamp"][timestamp].append(
            {
                "flow_id": self.flow.get("id")[:7],
                "message": message_str,
                "flow_name": self.flow_name,
                "error": error,
            }
        )

        self.logs["flow"]["logs"].append(
            {"message": message_str, "timestamp": timestamp, "error": error}
        )

    # Filter start nodes
    def filter_start_nodes(self):
        for node in self.nodes:
            node_obj = BaseNode(node)

            self.nodes_dict.update({node_obj.id: node_obj})

            if node_obj.is_start_node:
                self.start_nodes.append(node_obj.id)

    # Manager that manages a node and its children
    def node_and_children_manager(self, node_id: str):
        node = self.nodes_dict.get(node_id)

        node_manager = NodeManager(
            node,
            self.nodes_dict,
            self.lock,
            self.inputs,
            self.outputs,
            global_dict=self.global_dict,
            flow=self.flow,
            node_logger=self.node_logger,
        )
        node_manager.manage()

        children = node_manager.children

        with ThreadPoolExecutor(5) as executor:
            for child_id in children:
                future = executor.submit(self.node_and_children_manager, child_id)
                self.futures.append(future)

    # Execute the flow
    def manage(self):
        self.flow_logger("Flow Execution Started")

        self.filter_start_nodes()

        with ThreadPoolExecutor(5) as executor:
            for node_id in self.start_nodes:
                future = executor.submit(self.node_and_children_manager, node_id)
                self.futures.append(future)

        self.flow_logger("Flow Execution Completed")

        if self.execution_id is not None:
            self.save_logs()

    def save_logs(self):
        import requests
        import json
        import io

        url = f"{BACKEND_URL}/v2/archives/logs/"
        crr_time = datetime.now()

        year = crr_time.year
        month = crr_time.month
        day = crr_time.day
        hour = crr_time.hour
        minute = crr_time.minute
        second = crr_time.second
        json_file_name = f"{day}_{hour:02}:{minute:02}:{second:02}.json"

        json_data = json.dumps(self.logs)
        f = io.BytesIO(json_data.encode())

        res = requests.post(
            url,
            files={"file": (json_file_name, f)},
            data={
                "name": json_file_name,
                "flow": self.flow.get("id"),
                "timestamp_prefix": f"json/{year}/{month:02}",
            },
        )
        json_archive_id = res.json().get("id")

        from jinja2 import Environment, FileSystemLoader

        env = Environment(loader=FileSystemLoader(f"{BASE_DIR}/v2/templates"))
        template = env.get_template("logs.html")

        output = template.render(logs=self.logs)

        html_file_name = f"{day}_{hour:02}:{minute:02}:{second:02}.html"

        f = io.BytesIO(output.encode())

        res = requests.post(
            url,
            files={"file": (html_file_name, f)},
            data={
                "name": html_file_name,
                "flow": self.flow.get("id"),
                "timestamp_prefix": f"html/{year}/{month:02}",
            },
        )

        html_archive_id = res.json().get("id")

        requests.patch(
            f"{BACKEND_URL}/v2/flows/{self.flow.get('id')}/executions/",
            json={
                "id": self.execution_id,
                "json_logs": json_archive_id,
                "html_logs": html_archive_id,
            },
        )

    def wait_for_completion(self):
        for future in self.futures:
            future.result()
