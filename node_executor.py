from node_class_executor import NodeClassExecutor
from app_enums import NODE_ENUM, DATA_TYPE, NODE_CLASS_ENUM


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
        type = kwargs.get("type", None)
        value = kwargs.get("value", None)

        if type is None:
            raise Exception(f"Type is required for DataNode (id: {self.id})")

        if value is None:
            raise Exception(f"Value is required for DataNode (id: {self.id})")

        def get_data(type, value):
            match type:
                case DATA_TYPE.INTEGER:
                    return int(value)
                case DATA_TYPE.STRING:
                    return str(value)
                case DATA_TYPE.BOOLEAN:
                    return bool(value)
                case DATA_TYPE.FLOAT:
                    return float(value)
                case DATA_TYPE.LIST:
                    return list(value)
                case DATA_TYPE.SET:
                    return set(value)
                case DATA_TYPE.TUPLE:
                    return tuple(value)
                case DATA_TYPE.DICTIONARY:
                    return dict(value)
                case default:
                    raise Exception(f"Invalid type for DataNode (id: {self.id}")

        outputs = {}
        outputs["data"] = get_data(type, value)
        return outputs

    # execute the generic node
    def execute_generic_node(self, globals, locals, **kwargs):
        node_class_type: NODE_CLASS_ENUM = kwargs.get("node_class_type", None)
        triggered = kwargs.get("triggered", False)

        outputs = {}
        output_slots = kwargs.get("output_slots", [])
        node_class_name = kwargs.get("node_class_name", None)

        if node_class_type == NODE_CLASS_ENUM.TRIGGER_NODE_CLASS and triggered:
            # check cases for different trigger nodes
            match node_class_name:
                # Trigger Node class with name 'WebhookTriggerNode'
                case "WebhookTriggerNode":
                    # get data from triggered_data
                    data = kwargs.get("triggered_data", None)
                    if "data" not in output_slots:
                        raise Exception(
                            f"Output slot 'data' is required for Webhook triggered node: {self.id}"
                        )
                    outputs.update({"data": data})
                    return outputs

                # Trigger Node class with name 'PeriodicTriggerNode'
                case "PeriodicTriggerNode":
                    return outputs

                case default:
                    return outputs

        try:
            NodeClassExecutor(node_class_type=node_class_type, node_id=self.id).execute(
                globals, locals, **kwargs
            )
        except Exception as e:
            raise Exception(
                f'Error in executing generic node with node_class_type: {kwargs.get("node_class_type", None)}, error: {str(e)}'
            )

        if node_class_type == NODE_CLASS_ENUM.TRIGGER_NODE_CLASS and not triggered:
            output_slots = output_slots.copy()
            output_slots.remove("data")

        for slot in output_slots:
            if slot in locals:
                outputs.update({slot: locals[slot]})
            else:
                raise ValueError(
                    f"Slot is not found in function output, check values returned by function for node: {self.id}"
                )
        return outputs
