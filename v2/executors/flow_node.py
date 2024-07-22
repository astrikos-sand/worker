import requests

from v2.executors.base import Base
from v2.flow_manager import FlowManager

from config.const import BACKEND_URL


class InputNode(Base):
    def execute(self) -> dict:
        outputs = self.kwargs.get("flow_inputs")
        return outputs


class OutputNode(Base):
    def execute(self) -> dict:
        self.kwargs["flow_outputs"].update(self.inputs)
        outputs = self.inputs
        return outputs


class FlowNode(Base):
    def execute(self) -> dict:
        # TODO: Add interface for this
        res = requests.get(
            f"{BACKEND_URL}/v2/flow/{self.node.dict.get('represent').get('id')}/nodes/"
        )
        data = res.json()
        flow = data.get("flow")
        nodes = data.get("nodes")
        inputs = self.inputs

        flow_manager = FlowManager(flow, nodes, inputs)
        flow_manager.manage()
        outputs = flow_manager.outputs

        return outputs
