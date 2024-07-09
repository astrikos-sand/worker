from threading import Lock


class NodeManager:
    executors = {}

    @classmethod
    def register(cls, node_type: str, executor):
        cls.executors[node_type] = executor

    def __init__(self, node: dict, nodes_dict: dict, lock: Lock) -> None:
        self.node = node
        self.lock = lock
        self.nodes_dict = nodes_dict
        self.children = []

    @property
    def id(self) -> str:
        return self.node.get("id")

    @property
    def node_type(self) -> str:
        return self.node.get("node_type")

    @property
    def executor(self):
        return self.executors.get(self.node_type)

    @property
    def input_slots(self) -> list:
        return self.node.get("input_slots")

    @property
    def output_slots(self) -> list:
        return self.node.get("output_slots")

    @property
    def connections_in(self) -> list:
        return self.node.get("connections_in")

    @property
    def connections_out(self) -> list:
        return self.node.get("connections_out")

    @property
    def inputs(self) -> dict:
        return self.node.get("inputs", {})

    @property
    def input_slots_dict(self) -> dict:
        return {slot.get("id"): slot for slot in self.input_slots}

    @property
    def output_slots_dict(self) -> dict:
        return {slot.get("id"): slot for slot in self.output_slots}

    def is_ready_for_execution(self) -> bool:
        for connection in self.connections_in:
            source_id = connection.get("source")
            source = self.nodes_dict.get(source_id)

            if not source.get("executed", False):
                return False

        return True

    def manage(self):
        if self.is_ready_for_execution():
            # TODO: Need fix in this if statement
            # if not all(param in self.inputs for param in self.input_slots):
            #     raise Exception(
            #         f"All inputs are not available for node {self.id}, available inputs {self.inputs}, required inputs {self.input_slots}"
            #     )

            node_executor = self.executor(self.node, self.inputs)
            outputs = node_executor.execute()

            with self.lock:
                self.nodes_dict.get(self.id).update({"outputs": outputs})

            # TODO: Optimize it as we have slots id now - O(1)
            for connection in self.connections_out:
                target_id = connection.get("target", None)
                to_slot_id = connection.get("to_slot", None)
                from_slot_id = connection.get("from_slot", None)

                output = outputs.get(
                    self.output_slots_dict.get(from_slot_id).get("name"), None
                )

                with self.lock:
                    target_input_slots = self.nodes_dict.get(target_id).get(
                        "input_slots"
                    )
                    name = list(
                        filter(
                            lambda slot: slot.get("id") == to_slot_id,
                            target_input_slots,
                        )
                    )[0].get("name")

                    self.nodes_dict.get(target_id).setdefault("inputs", {}).update(
                        {name: output}
                    )

                self.children.append(target_id)

            with self.lock:
                self.nodes_dict.get(self.id).update({"executed": True})
