import requests
from config.enums import NODE_CLASS_ENUM
import config.const as const

class NodeClassExecutor:

    def __init__(self, node_class_type: NODE_CLASS_ENUM, node_id: str):
        self.node_class_type = node_class_type
        self.node_id = node_id

    def read_online_file(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an exception for HTTP errors (status codes >= 400)
            return response.text  # Return the content of the file as text
        except requests.RequestException as e:
            print(f"Error fetching file: {e}")
        return None

    def execute(self, globals, locals, **kwargs):
        code = kwargs.get("code", None)
        if code is None:
            raise Exception(
                f"Code is required for execution in a node class: {self.node_class_type} and node id: {self.node_id}"
            )
        code_url = code
        if const.DEBUG:
            media_part = code.split("/media/")[1]
            code_url = f"{const.BACKEND_URL}/media/{media_part}"
        code_text = self.read_online_file(code_url)
        exec(code_text, globals, locals)
        return locals
