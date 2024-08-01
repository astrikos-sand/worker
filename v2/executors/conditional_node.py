import requests

from v2.executors.base import Base
from v2.executors.utils import get_data

from v2.flow_manager import FlowManager
from config.const import BACKEND_URL


class ConditionalNode(Base):
    def execute(self) -> dict:
        inputs = self.inputs
        value_type = self.node.dict.get("value_type")

        condition = inputs.pop("_condition")
        condition_typecast_value = condition

        cases = self.node.dict.get("cases")
        match_case = None

        for case in cases:
            value = case.get("value")

            if value is None:
                default_case = case
                continue

            case_typecast_value = get_data(value_type, value)

            if condition_typecast_value == case_typecast_value:
                match_case = case
                break

        if not match_case:
            match_case = default_case

        flow_id = match_case.get("block").get("flow").get("id")
        res = requests.get(f"{BACKEND_URL}/v2/flow/{flow_id}/nodes/")
        data = res.json()

        flow = data.get("flow")
        nodes = data.get("nodes")
        inputs["_case"] = condition_typecast_value
        print(f"Matched case: {flow.get('name')}")
        flow_manager = FlowManager(flow, nodes, inputs)
        flow_manager.manage()
        outputs = flow_manager.outputs

        return outputs
