import requests

from v2.executors.base import Base
from v2.flow_manager import FlowManager


class ForEachNode(Base):
    def execute(self) -> dict:
        block = self.node.dict.get("block")
        flow_id = block.get("flow").get("id")
        res = requests.get(f"http://localhost:8000/v2/flow/{flow_id}/nodes/")
        data = res.json()

        flow = data.get("flow")
        nodes = data.get("nodes")

        inputs = self.inputs
        elements = inputs.pop("_list")
        input_keys = list(inputs.keys())

        for element in elements:
            inputs["_element"] = element
            flow_manager = FlowManager(flow, nodes, inputs)
            flow_manager.manage()
            outputs = flow_manager.outputs
            output_keys = list(outputs.keys())
            if not all([key in output_keys for key in input_keys]):
                break
            inputs = outputs

        outputs.pop("element")

        return outputs
