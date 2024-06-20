from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from config.enums import SUBMIT_TASK_TYPE
from tasks import submit_node_task
import sys
from utils.api import API
from config import const


def task_handler(data: dict):
    try:
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

    print(node_outputs, flush=True)

    # API(base_url=f"{const.BACKEND_URL}").post(
    #     "/tasks/save_outputs/",
    #     data={"success": True, "outputs": node_outputs},
    # )


if __name__ == "__main__":
    load_dotenv()
    data = sys.argv[1]
    import json

    data = json.loads(data)
    task_handler(data)
