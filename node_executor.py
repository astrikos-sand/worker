from strenum import StrEnum

from node_class_executor import NodeClassExecutor


class NodeExecutor:

    class NODE_ENUM(StrEnum):
        DATA_NODE = "DataNode"
        GENERIC_NODE = "GenericNode"

    def __init__(self, node_type: NODE_ENUM, id: str):
        self.node_type = node_type
        self.id = id

    def execute(self, globals, locals, **kwargs):
        print("Executing node:", self.id, "with type:", self.node_type)
        match self.node_type:
            case self.NODE_ENUM.DATA_NODE:
                return self.execute_data_node(globals, locals, **kwargs)
            case self.NODE_ENUM.GENERIC_NODE:
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

        class DATA_TYPE(StrEnum):
            INTEGER = ("INT",)
            STRING = ("STR",)
            BOOLEAN = ("BOOL",)
            FLOAT = ("FLOAT",)
            LIST = ("LIST",)
            SET = ("SET",)
            TUPLE = ("TUPLE",)
            DICTIONARY = "DICT"

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
        try:
            NodeClassExecutor(
                node_class_type=kwargs.get("node_class_type", None), node_id=self.id
            ).execute(globals, locals, **kwargs)
        except Exception as e:
            raise Exception(
                f'Error in executing generic node with node_class_type: {kwargs.get("node_class_type", None)}, error: {str(e)}'
            )

        outputs = {}
        output_slots = kwargs.get("output_slots", None)

        if output_slots is None:
            raise Exception(
                f"Output slots is required for generic node (node: {self.id})"
            )

        for slot in output_slots:
            if slot in locals:
                outputs.update({slot: locals[slot]})
            else:
                raise ValueError(
                    f"Slot is not found in function output, check values returned by function for node: {self.id}"
                )
        return outputs
