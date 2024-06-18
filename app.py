from flask import Flask, request

from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from config.enums import SUBMIT_TASK_TYPE
from config.const import DOCKER_SOCKET_PATH


load_dotenv()

import config.const as const
from tasks import submit_node_task

app = Flask(__name__)


@app.route("/", methods=["POST"])
def handle_task():
    try:
        data = request.json

        nodes = data.get("nodes", [])
        submit_type = data.get("type", SUBMIT_TASK_TYPE.NORMAL)
        nodes_dict = {}
        start_nodes = []

        for node in nodes:
            node_id = node.get("id", None)

            if node_id is None:
                raise Exception("Node id is required for every node")

            nodes_dict.update({node_id: node})

            # If normal execution then find all nodes with no input slots
            if submit_type == SUBMIT_TASK_TYPE.NORMAL:
                slots = node.get("input_slots", [])
                target_connections = node.get("target_connections", [])

                # if there is a connection with special slot then target_connection will not be empty when slot is empty
                if len(slots) == 0 and len(target_connections) == 0:
                    start_nodes.append(node_id)

        # if triggered execution then find the trigger node and start execution from there
        # also store any data recieved into triggered_data field
        triggered = False
        if submit_type == SUBMIT_TASK_TYPE.TRIGGERED:

            trigger_node_id = data.get("trigger_node", None)
            nodes_dict.get(trigger_node_id, {}).update({"triggered": True})
            triggered = True
            data = data.get("data", None)
            if trigger_node_id is None:
                raise Exception("Trigger node is required for triggered task")
            start_nodes = [trigger_node_id]
            # add triggered_data to trigger node
            if data:
                nodes_dict.setdefault(trigger_node_id, {}).update(
                    {"triggered_data": data}
                )

        with ThreadPoolExecutor(10) as executor:

            for node_id in start_nodes:
                submit_node_task(node_id, executor, nodes_dict, triggered=triggered)

    except Exception as e:
        print(f"Error: {str(e)}", flush=True)
        return {"error": str(e), "success": False}, 500

    node_outputs = {
        node_id: {
            "node_type": nodes_dict.get(node_id).get("node_type", None),
            "node_class_type": nodes_dict.get(node_id).get("node_class_type", None),
            "node_class_name": nodes_dict.get(node_id).get("node_class_name", None),
            "inputs": nodes_dict.get(node_id).get("inputs", {}),
            "outputs": nodes_dict.get(node_id).get(
                "outputs",
                {
                    "details": "No outputs found, it seems this node is scheduled to run in future."
                },
            ),
        }
        for node_id in nodes_dict
    }
    return {"success": True, "outputs": node_outputs}


@app.route("/env/", methods=["POST"])
def create_environment():
    data = request.json
    requirements = data.get("requirements")
    id = data.get("id")

    import docker
    from string import Template
    from io import BytesIO
    import json

    if const.DEBUG:
        media_part = requirements.split("/media/")[1]
        download_url = f"{const.BACKEND_URL}/media/{media_part}"

    template_file_path = f"{const.BASE_DIR}/environment/Dockerfile"
    script_path = f"{const.BASE_DIR}/environment/download_script.py"

    with open(script_path, "r") as file:
        script_content = file.read()

    with open(template_file_path, "r") as file:
        template = Template(file.read())
        dockerfile_content = template.substitute(
            download_url=download_url, download_script=json.dumps(script_content)
        )

    client = docker.DockerClient(base_url=DOCKER_SOCKET_PATH)
    image_tag = f"astrikos-environment-{id}"

    dockerfile_bytes = dockerfile_content.encode("utf-8")
    dockerfile_obj = BytesIO(dockerfile_bytes)

    client.images.build(
        fileobj=dockerfile_obj,
        tag=image_tag,
        rm=True,
        pull=True,
    )

    return {"success": True, "image_tag": image_tag}


if __name__ == "__main__":
    app.config["DEBUG"] = 1
    app.run(debug=1, host=const.HOST, port=const.PORT)
