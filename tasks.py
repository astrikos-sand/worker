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

speciality_output = {
    SLOT_SPECIALITY.SIGNAL: lambda: True,
}


def execute_node(node: dict, nodes_dict: dict[dict], triggered=False):    
    node_id = node.get("id", None)    
    if node_id is None:
        raise Exception("Node id is required for every node")
    
    node_class_type = node.get("node_class_type", None)
        
    if node_class_type != NODE_CLASS_ENUM.TRIGGER_NODE_CLASS and triggered:
        raise Exception("Triggered is True for a non trigger node class")
    
    input_slots = node.get("input_slots", [])
    inputs = nodes_dict.get(node_id).get("inputs", {}).copy()
    
    globals = {}
    children = []
    
    print("exceuting node", node_id, node.get("node_class_type"), inputs, input_slots, flush=True)
    
    # update input with the stored input from backend (TODO: update this with the actual input)
    
    if all(param in inputs for param in input_slots):
        
        print(f"execution start for {node_id}", flush=True)
        node_type = node.get("node_type", None)
        
        node_executor = NodeExecutor(id=node_id, node_type=node_type)
        
        output_slots = node.get("output_slots", [])
        delayed_output_slots = node.get("delayed_output_slots", [])
        
        special_slots = node.get("special_slots", [])
        delayed_special_output_slots = node.get("delayed_special_output_slots", [])
        
        special_input_slots = filter(lambda slot: slot.get("attachment_type", None) == SLOT_ATTACHMENT_TYPE.INPUT, special_slots)
        special_output_slots = filter(lambda slot: slot.get("attachment_type", None) == SLOT_ATTACHMENT_TYPE.OUTPUT, special_slots)
        
        execution_signal = True

        for special_input in special_input_slots:
            speciality: SLOT_SPECIALITY = special_input.get("speciality", None)
            name: str = special_input.get("name", None)
            match speciality:
                case SLOT_SPECIALITY.NODE_ID:
                    inputs.update({name: node_id})
                case SLOT_SPECIALITY.SIGNAL:
                    execution_signal = inputs.get(name, True) # if signal parameter exists then assign execution signal to that value otherwise always true
                case _:
                    special_input_fn = speciality_input.get(speciality, None)
                    if special_input is not None:
                        inputs.update({name: special_input_fn()})
                    else:
                        raise Exception(f"Invalid speciality for input slot: speciality: {speciality} name: {name}")
                    
        if not execution_signal:
            return children # empty list when there is no execution signal
        
        outputs = node_executor.execute(globals, inputs, triggered=triggered, **node)
        with node_dict_lock:
            nodes_dict.get(node.get("id")).update({"outputs": outputs})
            
        extract_special_outputs = lambda slots: dict((slot.get("name", None), slot.get("speciality", None)) for slot in slots)
            
        functional_output_slots = output_slots if not triggered else delayed_output_slots
        functional_special_output_slots = special_output_slots if not triggered else delayed_special_output_slots
        functional_special_output_slots = extract_special_outputs(functional_special_output_slots) # convert into key value pair dict
        
        print(f"functional output slots {functional_output_slots} functional special output slots {functional_special_output_slots}", flush=True)
        
        source_connections = node.get("source_connections", [])
        
        for connection in source_connections:
            target_node_id = connection.get("target", None)
            target_slot = connection.get("target_slot", None)
            source_slot = connection.get("source_slot", None)
            output_present = False
            if source_slot in functional_special_output_slots.keys():
                functional_special_output_fn = speciality_output.get(functional_special_output_slots.get(source_slot), lambda : None)
                output = functional_special_output_fn()
                print(f"output for {source_slot} is {output}", flush=True)
                output_present =True
            elif source_slot in functional_output_slots:
                output = outputs.get(source_slot, None)
                output_present = True
                
            if output_present:
                with node_dict_lock:
                    print(f"update inputs for {target_node_id}, {target_slot} to {output}", flush=True)
                    nodes_dict.get(target_node_id).setdefault("inputs", {}).update({target_slot: output})
                children.append(target_node_id)
        
    children = list(set(children))
    return children


def submit_node_task(node_id, executor, nodes_dict: dict[dict], triggered=False):
    node = nodes_dict.get(node_id, None)
    future = executor.submit(execute_node, node, nodes_dict, triggered=triggered)

    # raises error when there is any error in execution
    children = future.result()

    for child_id in children:
        # When parent is triggered then childs are not triggered ( default value of triggered is False )
        submit_node_task(child_id, executor, nodes_dict)
