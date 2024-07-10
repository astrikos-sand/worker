import requests

from v2.executors.base import Base
import config.const as const


class FunctionNode(Base):
    def read_online_file(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def execute_code(self):
        code = self.node.dict.get("definition").get("code", None)
        if code is None:
            raise Exception(
                f"Code is required for execution in a node class: {self.node_class_type} and node id: {self.node_id}"
            )
        code_url = code
        if const.DEBUG:
            media_part = code.split("/media/")[1]
            code_url = f"{const.BACKEND_URL}/media/{media_part}"

        code_text = self.read_online_file(code_url)

        globals = {}
        locals = self.inputs
        exec(code_text, globals, locals)
        return locals

    def execute(self) -> dict:
        output_slots = self.node.output_slots

        try:
            locals = self.execute_code()
        except Exception as e:
            raise Exception(
                f"Error in executing function: {self.node.dict.get('definition').get('name')}, node id{self.node.id}, error: {str(e)}"
            )

        outputs = {}

        for slot in output_slots:
            name = slot.get("name")
            if name in locals:
                outputs.update({name: locals[name]})
            else:
                raise ValueError(
                    f"Slot is not found in function output, check values returned by function for node: {self.node.get('id')}"
                )

        return outputs
