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

        requirements_url = "http://backend:8000/media/flow/environments/requirements.txt"

        requirements = self.read_online_file(requirements_url)
        code_text = self.read_online_file(code_url)

        import docker
        import json

        serialized_globals = json.dumps(globals)
        serialized_locals = json.dumps(locals)

        client = docker.DockerClient(base_url="unix://var/run/docker.sock")

        code_string = """
import os

locals = {locals}
globals = {globals}

code_file_path = "/app/code.py"

with open(code_file_path, "r") as file:
    code = file.read()
    exec(code, globals, locals)

    print(locals, flush=True)
""".format(
            locals=serialized_locals, globals=serialized_globals
        )

        dockerfile_content = """
FROM python:3.10.6-slim

WORKDIR /app

ARG VARIABLE_1={requirements}

RUN echo $VARIABLE_1 > ./requirements.txt
RUN pip install -r requirements.txt

ARG VARIABLE_2={code_string}
ARG VARIABLE_3={code_text}

RUN echo $VARIABLE_2 > ./main.py
RUN echo $VARIABLE_3 > ./code.py

CMD ["python", "main.py"]
""".format(
            code_text=json.dumps(code_text),
            code_string=json.dumps(code_string),
            requirements=json.dumps(requirements),
        )

        image_tag = "astrikos-environment"

        dockerfile_bytes = dockerfile_content.encode("utf-8")

        from io import BytesIO

        # Create a file-like object using BytesIO
        dockerfile_obj = BytesIO(dockerfile_bytes)

        # Build the Docker image
        client.images.build(
            fileobj=dockerfile_obj,
            tag=image_tag,
            rm=True,
            pull=True,
        )

        container = client.containers.run(
            image_tag,
            network="astrikos-workspace_worker",
            detach=True,
        )

        container.wait()
        logs = container.logs().decode("utf-8")
        container.remove()

        print(logs, flush=True)

        locals = logs.split("\n")[-2]
        return locals
