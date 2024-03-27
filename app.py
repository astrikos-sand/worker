from flask import Flask, request

from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

import const
from tasks import submit_node_task

app = Flask(__name__)


@app.route("/", methods=["POST"])
def handle_task():
    try:
        data = request.json
        nodes = data.get("nodes", [])
        nodes_dict = {}
        start_nodes = []

        for node in nodes:
            node_id = node.get("id", None)

            if node_id is None:
                raise Exception("Node id is required for every node")

            nodes_dict.update({node_id: node})
            slots = node.get("input_slots", None)

            if slots is None:
                raise Exception(f"Input slots is null for node: {node_id}")

            if len(slots) == 0:
                start_nodes.append(node_id)

        with ThreadPoolExecutor(10) as executor:

            for node_id in start_nodes:
                submit_node_task(node_id, executor, nodes_dict)

    except Exception as e:
        return {"error": str(e), "success": False}

    node_outputs = {
        node_id: {"outputs": nodes_dict.get(node_id).get("outputs", {})}
        for node_id in nodes_dict
    }
    return {"success": True, "outputs": node_outputs}


if __name__ == "__main__":
    app.config["DEBUG"] = const.DEBUG
    app.run(debug=const.DEBUG, host=const.HOST, port=const.PORT)
