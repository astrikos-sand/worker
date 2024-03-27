from node_executor import NodeExecutor

from threading import Lock

from db import DB

parameter_map: dict[dict] = {}
lock = Lock()
node_dict_lock = Lock()


def execute_node(node, nodes_dict):
    # fetch parameters
    print("node:", node.get("id"))
    inputs = parameter_map.get(node.get("id"), {})  # id is non nullable
    input_slots = node.get("input_slots")  # input slot is non nullable

    globals = {}
    children = []

    # if all input parameters exist then execute the node and submit all child not execute node, else return

    if all(param in inputs for param in input_slots):
        # execute the node
        node_executor = NodeExecutor(
            node_type=node.get("node_type", None), id=node.get("id")
        )
        
        special_slots = node.get("special_slots", [])
        if special_slots:
            for special_slot in special_slots:
                if special_slot.get("speciality") == "DB":
                    inputs.update({special_slot.get("name"): DB()})
                    
        outputs = node_executor.execute(globals, inputs, **node)

        with node_dict_lock:
            nodes_dict.get(node.get("id")).update({"outputs": outputs})
        # for all output parameters, update the parameter map and submit the child nodes for execution
        source_connections = node.get("source_connections", [])
        for connection in source_connections:
            target_node_id = connection.get("target", None)
            target_slot = connection.get("target_slot", None)
            output = outputs.get(connection.get("source_slot", None), None)

            with lock:
                parameter_map.setdefault(target_node_id, {}).update(
                    {target_slot: output}
                )

            children.append(target_node_id)

    return children


def submit_node_task(node_id, executor, nodes_dict):
    node = nodes_dict.get(node_id, None)
    future = executor.submit(execute_node, node, nodes_dict)

    # raises error when there is any error in execution
    children = future.result()

    for child_id in children:
        submit_node_task(child_id, executor, nodes_dict)
