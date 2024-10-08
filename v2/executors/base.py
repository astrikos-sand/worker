from v2.node import BaseNode


class Base:
    def __init__(
        self, node: BaseNode, inputs, lock, nodes_dict: dict[str, BaseNode], **kwargs
    ) -> None:
        self.node = node
        self.inputs = inputs
        self.lock = lock
        self.nodes_dict = nodes_dict
        self.children = []
        self.kwargs = kwargs
        self.global_dict: dict = self.kwargs.get("global_dict")
        self.flow: dict = self.kwargs.get("flow")
        self.node_logger = self.kwargs.get("node_logger")

    def execute(self) -> dict:
        raise NotImplementedError

    def is_ready_for_execution(self, node: BaseNode) -> bool:
        if not all(
            param in node.inputs for param in list(node.input_slots_names.keys())
        ):
            return False

        return True

    def manage(self):
        self.node_logger(self.node.id, "Execution started")

        outputs = self.execute()

        with self.lock:
            self.nodes_dict.get(self.node.id).outputs = outputs

            for connection in self.node.connections_out:
                target_id = connection.get("target", None)
                to_slot_id = connection.get("to_slot", None)
                from_slot_id = connection.get("from_slot", None)

                output_name = self.node.output_slots_dict.get(from_slot_id).get("name")

                if output_name not in outputs:
                    continue

                output = outputs.get(output_name)

                target_input_slots = self.nodes_dict.get(target_id).input_slots
                name = list(
                    filter(
                        lambda slot: slot.get("id") == to_slot_id,
                        target_input_slots,
                    )
                )[0].get("name")

                self.nodes_dict.get(target_id).inputs[name] = output

                target = self.nodes_dict.get(target_id)
                if self.is_ready_for_execution(target):
                    self.children.append(target_id)

        if len(str(outputs)) < 500:
            self.node_logger(self.node.id, f"Executed with outputs {outputs}")
        else:
            self.node_logger(
                self.node.id, f"Executed with outputs of length {len(str(outputs))}"
            )

        self.node_logger(self.node.id, "Execution finished")
