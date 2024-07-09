class Base:
    def __init__(self, node, inputs) -> None:
        self.node = node
        self.inputs = inputs

    def execute(self) -> dict:
        raise NotImplementedError
