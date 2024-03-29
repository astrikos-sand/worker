from flask import Flask, request

from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from app_enums import SUBMIT_TASK_TYPE
import asyncio

load_dotenv()

import const
from tasks import submit_node_task

app = Flask(__name__)


@app.route("/", methods=["POST"])
def handle_task():
    try:
        data = request.json
        nodes = data.get("nodes", [])
        type = data.get("type", SUBMIT_TASK_TYPE.NORMAL)

        nodes_dict = {}
        start_nodes = []

        for node in nodes:
            node_id = node.get("id", None)

            if node_id is None:
                raise Exception("Node id is required for every node")

            nodes_dict.update({node_id: node})

            # If normal execution then find all nodes with no input slots
            if type == SUBMIT_TASK_TYPE.NORMAL:
                slots = node.get("input_slots", None)
                target_connections = node.get("target_connections", [])

                if slots is None:
                    raise Exception(f"Input slots is null for node: {node_id}")

                if len(slots) == 0 and len(target_connections) == 0:
                    start_nodes.append(node_id)

        # if triggered execution then find the trigger node and start execution from there

        # also store any data recieved into triggered_data field
        triggered = False
        if type == SUBMIT_TASK_TYPE.TRIGGERED:
            
            trigger_node_id = data.get("trigger_node", None)
            print(f'triggered execution for node {trigger_node_id}', flush=True)
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
        return {"error": str(e), "success": False}

    node_outputs = {
        node_id: {
            "outputs": nodes_dict.get(node_id).get(
                "outputs",
                {
                    "details": "No outputs found, it seems this node is scheduled to run in future."
                },
            )
        }
        for node_id in nodes_dict
    }
    return {"success": True, "outputs": node_outputs}


if __name__ == "__main__":
    app.config["DEBUG"] = const.DEBUG
    app.run(debug=const.DEBUG, host=const.HOST, port=const.PORT)
