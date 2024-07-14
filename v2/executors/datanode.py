from v2.executors.base import Base
from v2.executors.utils import get_data


# TODO: Implement typecast at slot level
class DataNode(Base):
    def execute(self) -> dict:
        value = self.node.dict.get("value", None)
        output_slot = self.node.output_slots[0].get("name")
        value_type = self.node.output_slots[0].get("value_type")
        typecast_value = get_data(value_type, value)
        return {output_slot: typecast_value}
