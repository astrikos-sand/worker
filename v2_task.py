from dotenv import load_dotenv


def task_handler(data):
    from v2.flow_manager import FlowManager
    from v2.subscribe import register_executors

    register_executors()

    nodes = data.get("nodes", [])
    flow = data.get("flow", {})
    inputs = data.get("inputs", {})
    execution_id = data.get("execution_id")

    flow_manager = FlowManager(
        flow=flow, nodes=nodes, inputs=inputs, execution_id=execution_id
    )
    flow_manager.manage()


if __name__ == "__main__":
    load_dotenv()
    import json

    with open("data.json") as f:
        data = json.load(f)

    task_handler(data)
