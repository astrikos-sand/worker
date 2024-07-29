import requests

from v2.executors.base import Base
from v2.flow_manager import FlowManager

from config.const import BACKEND_URL


class BlockNode(Base):
    def execute(self) -> dict:
        block = self.node.dict.get("block")
        flow_id = block.get("flow").get("id")
        res = requests.get(f"{BACKEND_URL}/v2/flow/{flow_id}/nodes/")
        data = res.json()

        flow = data.get("flow")
        nodes = data.get("nodes")

        inputs = self.inputs

        flow_manager = FlowManager(flow, nodes, inputs)
        flow_manager.manage()
        outputs = flow_manager.outputs

        return outputs
