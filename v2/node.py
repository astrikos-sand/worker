from v2.mappings import NODE_TYPE


class BaseNode:
    def __init__(self, node_dict: dict):
        self.id: str = node_dict.pop("id")
        self.node_type: str = node_dict.pop("node_type")
        self.input_slots: list[dict] = node_dict.pop("input_slots", [])
        self.output_slots: list[dict] = node_dict.pop("output_slots", [])
        self.connections_in: list[dict] = node_dict.pop("connections_in", [])
        self.connections_out: list[dict] = node_dict.pop("connections_out", [])
        self.inputs: dict = node_dict.pop("inputs", {})
        self.outputs: dict = node_dict.pop("outputs", {})
        self.executed: bool = node_dict.pop("executed", False)

        self.input_slots_dict: dict = {}
        self.input_slots_names: dict[str, str] = {}

        for slot in self.input_slots:
            self.input_slots_dict[slot.get("id")] = slot
            self.input_slots_names[slot.get("name")] = slot.get("id")

        self.output_slots_dict: dict = {}
        self.output_slots_names: dict[str, str] = {}

        for slot in self.output_slots:
            self.output_slots_dict[slot.get("id")] = slot
            self.output_slots_names[slot.get("name")] = slot.get("id")

        self.dict = node_dict

    def __str__(self) -> str:
        node_id = self.id[:7]
        match self.node_type:
            case NODE_TYPE.DATA.value:
                return f"{self.node_type} {self.dict.get('name')} ({node_id})"

            case NODE_TYPE.FUNCTION.value:
                definition = self.dict.get("definition")
                definition_name = definition.get("name")

                if definition.get("prefix") is not None:
                    definition_name = (
                        f"{definition.get('prefix').get('full_name')}/{definition_name}"
                    )

                return f"{self.node_type} {definition_name} ({node_id})"

            case NODE_TYPE.FLOW.value:
                represent = self.dict.get("represent")
                represent_name = represent.get("name")
                if represent.get("prefix") is not None:
                    represent_name = (
                        f"{represent.get('prefix').get('full_name')}/{represent_name}"
                    )

                return f"{self.node_type} -> {represent_name} ({node_id})"

            case NODE_TYPE.INPUT.value:
                return f"{self.node_type} {node_id}"

            case NODE_TYPE.OUTPUT.value:
                return f"{self.node_type} {node_id}"

            case _:
                return f"{self.node_type} {node_id}"

    @property
    def details(self) -> dict:
        match self.node_type:
            case NODE_TYPE.DATA.value:
                return {
                    "name": self.dict.get("name"),
                    "value": self.dict.get("value"),
                    "value_type": self.dict.get("value_type"),
                }

            case NODE_TYPE.FUNCTION.value:
                definition = self.dict.get("definition")
                definition_name = definition.get("name")

                if definition.get("prefix") is not None:
                    definition_name = (
                        f"{definition.get('prefix').get('full_name')}/{definition_name}"
                    )

                return {
                    "name": definition_name,
                    "code": definition.get("code"),
                }

            case NODE_TYPE.FLOW.value:
                represent = self.dict.get("represent")
                represent_name = represent.get("name")
                if represent.get("prefix") is not None:
                    represent_name = (
                        f"{represent.get('prefix').get('full_name')}/{represent_name}"
                    )

                return {
                    "name": represent_name,
                }

            case NODE_TYPE.INPUT.value:
                return {}

            case NODE_TYPE.OUTPUT.value:
                return {}
