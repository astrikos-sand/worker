from v2.executors.base import Base
from v2.executors.utils import get_data


class ConditionalNode(Base):
    def execute(self) -> dict:
        inputs = self.inputs
        input_slot = self.node.input_slots[0]
        value_type = input_slot.get("value_type")
        value = inputs.get(input_slot.get("name"))
        typecast_value = get_data(value_type, value)

        output_slots = self.node.output_slots
        output_values = self.node.dict.get("values")

        triggered_slot = None
        outputs = {}

        for output_slot in output_slots:
            output_value = output_values.get(output_slot.get("name"))
            value_type = output_slot.get("value_type")
            typecast_output_value = get_data(value_type, output_value)
            outputs[output_slot.get("name")] = typecast_output_value
            if typecast_value == typecast_output_value:
                triggered_slot = output_slot

        return outputs
