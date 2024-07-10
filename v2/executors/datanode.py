from v2.executors.base import Base


# TODO: Implement typecast at serializer level
class DataNode(Base):
    def execute(self) -> dict:
        value = self.node.dict.get("value", None)
        output_slot = self.node.output_slots[0].get("name")
        return {output_slot: value}
