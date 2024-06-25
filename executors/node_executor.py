from executors.node_class_executor import NodeClassExecutor
from config.enums import NODE_ENUM, DATA_TYPE, NODE_CLASS_ENUM
from ast import literal_eval


class NodeExecutor:

    def __init__(self, node_type: NODE_ENUM, id: str):
        self.node_type = node_type
        self.id = id

    def execute(self, globals, locals, **kwargs):
        match self.node_type:
            case NODE_ENUM.DATA_NODE:
                return self.execute_data_node(globals, locals, **kwargs)
            case NODE_ENUM.GENERIC_NODE:
                return self.execute_generic_node(globals, locals, **kwargs)
            case default:
                raise Exception(f"Invalid node type for node {self.id}")

    # execute the data node
    def execute_data_node(self, globals, locals, **kwargs):
        data_type = kwargs.get("type", None)
        value = kwargs.get("value", None)

        if data_type is None:
            raise Exception(f"Type is required for DataNode (id: {self.id})")

        if value is None:
            raise Exception(f"Value is required for DataNode (id: {self.id})")

        def get_data(data_type, value):
            match data_type:
                case DATA_TYPE.INTEGER:
                    return int(value)
                case DATA_TYPE.STRING:
                    return str(value)
                case DATA_TYPE.BOOLEAN:
                    return bool(value)
                case DATA_TYPE.FLOAT:
                    return float(value)
                case DATA_TYPE.LIST:
                    value = literal_eval(value)
                    if type(value) is not list:
                        raise f"Invalid type of data node {self.id}, given list but got {type(value)}"
                    return value
                case DATA_TYPE.SET:
                    value = literal_eval(value)
                    if type(value) is not set:
                        raise f"Invalid type of data node {self.id}, given set but got {type(value)}"
                    return value
                case DATA_TYPE.TUPLE:
                    value = literal_eval(value)
                    if type(value) is not tuple:
                        raise f"Invalid type of data node {self.id}, given tuple but got {type(value)}"
                    return value
                case DATA_TYPE.DICTIONARY:
                    value = literal_eval(value)
                    if type(value) is not dict:
                        raise f"Invalid type of data node {self.id}, given dict but got {type(value)}"
                    return value
                case DATA_TYPE.NONE:
                    return None
                case default:
                    raise Exception(f"Invalid type for DataNode (id: {self.id}")

        outputs = {}
        outputs["data"] = get_data(data_type, value)
        return outputs

    # execute the generic node
    def execute_generic_node(self, globals, locals, **kwargs):
        node_class_type: NODE_CLASS_ENUM = kwargs.get("node_class_type", None)
        triggered = kwargs.get("triggered", False)

        outputs = {}
        output_slots = kwargs.get("output_slots", [])
        delayed_output_slots = kwargs.get("delayed_output_slots", [])
        triggered_data = kwargs.get("triggered_data", None)

        if node_class_type == NODE_CLASS_ENUM.TRIGGER_NODE_CLASS and triggered:
            # when trigger node is triggered, return only delayed output slots
            if all(param in triggered_data for param in delayed_output_slots):
                outputs = {
                    slot: triggered_data.get(slot) for slot in delayed_output_slots
                }
            else:
                raise Exception(
                    f"data is missing some field from {delayed_output_slots}"
                )
            return outputs

        try:
            NodeClassExecutor(node_class_type=node_class_type, node_id=self.id).execute(
                globals, locals, **kwargs
            )
        except Exception as e:
            raise Exception(
                f'Error in executing generic node with node_class_type: {kwargs.get("node_class_type", None)}, node id{self.id}, error: {str(e)}'
            )

        for slot in output_slots:
            if slot in locals:
                outputs.update({slot: locals[slot]})
            else:
                raise ValueError(
                    f"Slot is not found in function output, check values returned by function for node: {self.id}"
                )
        return outputs
