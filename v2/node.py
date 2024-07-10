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
