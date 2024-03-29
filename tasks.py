from node_executor import NodeExecutor

from threading import Lock

from db import DB
from api import API
from app_enums import SLOT_SPECIALITY, SLOT_ATTACHMENT_TYPE, NODE_CLASS_ENUM, NODE_ENUM
from const import BACKEND_URL

parameter_map: dict[dict] = {}
lock = Lock()
node_dict_lock = Lock()

speciality_input = {
    SLOT_SPECIALITY.DATABASE: lambda: DB(),
    SLOT_SPECIALITY.API: lambda: API,
    SLOT_SPECIALITY.BACKEND: lambda: API(base_url=BACKEND_URL),
    SLOT_SPECIALITY.NODE_ID: lambda: None,
}


def execute_node(node, nodes_dict, triggered=False):
    # fetch parameters
    inputs = parameter_map.get(node.get("id"), {})  # id is non nullable
    input_slots = node.get("input_slots")  # input slot is non nullable

    globals = {}
    children = []

    # if all input parameters exist then execute the node and submit all child not execute node, else return
    # triggered execution node should not wait for inputs
    node_type = node.get("node_type", None)
    node_class_type = node.get("node_class_type", None)
        
    if all(param in inputs for param in input_slots) or triggered:
        # execute the node
        node_executor = NodeExecutor(
            node_type=node_type, id=node.get("id")
        )
        

        special_slots = node.get("special_slots", [])

        # update all special slots with input speciality
        if special_slots:
            for special_slot in special_slots:
                speciality = special_slot.get("speciality", None)
                name = special_slot.get("name", None)
                attachment_type = special_slot.get("attachment_type", None)
                if attachment_type == SLOT_ATTACHMENT_TYPE.INPUT:
                    match speciality:
                        case SLOT_SPECIALITY.NODE_ID:
                            inputs.update({name: node.get("id")})
                        case SLOT_SPECIALITY.SIGNAL:
                            pass
                        case default:
                            print('speciality_input:', speciality, input, flush=True)
                            getter = speciality_input.get(speciality, None)
                            if getter is not None:
                                inputs.update(
                                    {name: getter()}
                                )
                            else:
                                raise Exception(f"Invalid speciality for input slot: speciality: {speciality} name: {name} attachment type: {attachment_type}")

        outputs = node_executor.execute(globals, inputs, triggered=triggered, **node)
        with node_dict_lock:
            nodes_dict.get(node.get("id")).update({"outputs": outputs})
        # for all output parameters, update the parameter map and submit the child nodes for execution

        node_class_type: NODE_CLASS_ENUM = node.get("node_class_type", None)
        # IMPORTANT! if node class is a trigger node and triggered is False then return
        if node_class_type == NODE_CLASS_ENUM.TRIGGER_NODE_CLASS and not triggered:
            return []  # do not execute further if trigger node is not triggered

        if node_class_type != NODE_CLASS_ENUM.TRIGGER_NODE_CLASS and triggered:
            raise Exception("Triggered is True for a non trigger node class")

        # get dict of all special output slots name and speciality
        special_output_slots = dict(
            (slot.get("name", None), slot.get("speciality", None))
            for slot in node.get("special_slots", [])
            if special_slot.get("attachment_type", None) == SLOT_ATTACHMENT_TYPE.OUTPUT
        ) if not triggered else dict(
            (slot.get("name", None), slot.get("speciality", None))
            for slot in node.get("delayed_special_output_slots", [])
        )

        source_connections = node.get("source_connections", [])
        for connection in source_connections:
            target_node_id = connection.get("target", None)
            target_slot = connection.get("target_slot", None)
            source_slot = connection.get("source_slot", None)

            if source_slot in special_output_slots.keys():
                if special_output_slots.get(source_slot) == SLOT_SPECIALITY.SIGNAL:
                    pass  # do nothing when special output is signal
            else:
                output = outputs.get(source_slot, None)
                with lock:
                    parameter_map.setdefault(target_node_id, {}).update(
                        {target_slot: output}
                    )
                
            children.append(target_node_id)

        # remove duplicate entries
        children = list(set(children))

    return children


def submit_node_task(node_id, executor, nodes_dict, triggered=False):
    node = nodes_dict.get(node_id, None)
    future = executor.submit(execute_node, node, nodes_dict, triggered=triggered)

    # raises error when there is any error in execution
    children = future.result()

    for child_id in children:
        # When parent is triggered then childs are not triggered ( default value of triggered is False )
        submit_node_task(child_id, executor, nodes_dict)
