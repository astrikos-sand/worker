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

    def execute(self) -> dict:
        raise NotImplementedError

    def manage(self):

        outputs = self.execute()

        with self.lock:
            self.nodes_dict.get(self.node.id).outputs = outputs

        # TODO: Optimize it as we have slots id now - O(1)
        for connection in self.node.connections_out:
            target_id = connection.get("target", None)
            to_slot_id = connection.get("to_slot", None)
            from_slot_id = connection.get("from_slot", None)

            output_name = self.node.output_slots_dict.get(from_slot_id).get("name")

            if output_name not in outputs:
                continue

            output = outputs.get(output_name)

            with self.lock:
                target_input_slots = self.nodes_dict.get(target_id).input_slots
                name = list(
                    filter(
                        lambda slot: slot.get("id") == to_slot_id,
                        target_input_slots,
                    )
                )[0].get("name")

                self.nodes_dict.get(target_id).inputs[name] = output

            self.children.append(target_id)

        print(f"Node {self.node.id} executed with outputs {outputs}")
