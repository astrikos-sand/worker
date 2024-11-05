import requests

from v2.executors.base import Base
import config.const as const


class FunctionImport:
    def __init__(self, func_path, func_refer: "FunctionNode"):
        self.func_path = func_path
        self.func_refer = func_refer
        self.function = self.get_function()
        self.code_text = self.get_code()

    def get_function(self):
        response = requests.get(f"{const.BACKEND_URL}/v2/functions/p/?path={self.func_path}")
        response.raise_for_status()
        return response.json()
    
    def get_code(self):
        code_url = self.url
        if const.DEBUG:
            media_part = self.url.split("/media/")[1]
            code_url = f"{const.BACKEND_URL}/media/{media_part}"

        return self.func_refer.read_online_file(code_url)
    
    @property
    def url(self):
        return self.function.get("code")
    
    def __call__(self, *args, **kwargs):
        globals = {
            "_get_global": self.func_refer.get_global,
            "_set_global": self.func_refer.set_global,
            "_globals": self.func_refer.get_globals,
            "_BACKEND_URL": const.BACKEND_URL,
            "_NODE_ID": self.func_refer.node.id,
            "_FLOW_ID": self.func_refer.flow.get("id"),
            "_logger": self.func_refer.logger,
            "_import_func": FunctionImport,
        }
        locals = kwargs
        exec(self.code_text, globals, locals)
        fields = self.function.get("fields")
        output = {}

        for field in fields:
            if field.get("attachment_type") == "OUT" and field.get("name") in locals:
                output.update({field.get("name"): locals.get(field.get("name"))})

        return output


class FunctionNode(Base):
    def logger(self, *messages, error=False):
        for message in messages:
            self.node_logger(self.node.id, message, error=error)

    def read_online_file(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def get_globals(self):
        return self.global_dict.get("globals")

    def get_global(self, key):
        return self.global_dict.get("globals").get(key, None)

    def set_global(self, key, value):
        with self.global_dict.get("lock"):
            self.global_dict.get("globals").update({key: value})

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

        globals = {
            "_get_global": self.get_global,
            "_set_global": self.set_global,
            "_globals": self.get_globals,
            "_BACKEND_URL": const.BACKEND_URL,
            "_NODE_ID": self.node.id,
            "_FLOW_ID": self.flow.get("id"),
            "_logger": self.logger,
            "_import_func": lambda path: FunctionImport(path, self),
        }
        locals = self.inputs
        exec(code_text, globals, locals)
        return locals

    def execute(self) -> dict:
        output_slots = self.node.output_slots

        try:
            locals = self.execute_code()
        except Exception as e:
            self.logger(str(e), error=True)
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
