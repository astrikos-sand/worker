from executors.node_executor import NodeExecutor

from threading import Lock

from utils.db import DB
from utils.api import API
from config.enums import SLOT_SPECIALITY, SLOT_ATTACHMENT_TYPE, NODE_CLASS_ENUM, NODE_ENUM
from config.const import BACKEND_URL

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
    
    ready_for_execution = True
    if not triggered:
        target_connections = node.get("target_connections", [])
        for connection in target_connections:
            source_node = connection.get("source", None)
            source_slot = connection.get("source_slot", None)
            source = nodes_dict.get(source_node, None)
            if source and not source.get("executed", False):
                ready_for_execution = False
                break
            
            source_delayed_output_slots = source.get("delayed_output_slots", [])
            source_delayed_special_output_slots = source.get("delayed_special_output_slots", [])
            source_total_delayed_slots = source_delayed_special_output_slots + source_delayed_output_slots
            source_triggered = source.get("triggered", False)
            if not source_triggered and source_slot in source_total_delayed_slots:
                ready_for_execution = False
                break
            
    if ready_for_execution:
        if not all(param in inputs for param in input_slots):
            raise Exception(f"All inputs are not available for node {node_id}, available inputs {inputs}, required inputs {input_slots}")
        
        node_type = node.get("node_type", None)
        
        node_executor = NodeExecutor(id=node_id, node_type=node_type)
        
        output_slots = node.get("output_slots", [])
        delayed_output_slots = node.get("delayed_output_slots", [])
        
        special_slots = node.get("special_slots", [])
        delayed_special_output_slots = node.get("delayed_special_output_slots", [])
        
        special_input_slots = filter(lambda slot: slot.get("attachment_type", None) == SLOT_ATTACHMENT_TYPE.INPUT, special_slots)
        special_output_slots = filter(lambda slot: slot.get("attachment_type", None) == SLOT_ATTACHMENT_TYPE.OUTPUT, special_slots)
        
        execution_signal = True
        signal_slot = None

        for special_input in special_input_slots:
            speciality: SLOT_SPECIALITY = special_input.get("speciality", None)
            name: str = special_input.get("name", None)
            match speciality:
                case SLOT_SPECIALITY.NODE_ID:
                    inputs.update({name: node_id})
                case SLOT_SPECIALITY.SIGNAL:
                    signal_slot = name
                    execution_signal = inputs.get(name, False) # if signal parameter exists then assign execution signal to that value otherwise always true
                case _:
                    special_input_fn = speciality_input.get(speciality, None)
                    if special_input is not None:
                        inputs.update({name: special_input_fn()})
                    else:
                        raise Exception(f"Invalid speciality for input slot: speciality: {speciality} name: {name}")
                    
        if not execution_signal:
            return children # empty list when there is no execution signal
        
        if signal_slot is not None:
            inputs.update({signal_slot: False})
        outputs = node_executor.execute(globals, inputs, triggered=triggered, **node)
        with node_dict_lock:
            nodes_dict.get(node.get("id")).update({"outputs": outputs})
            
        extract_special_outputs = lambda slots: dict((slot.get("name", None), slot.get("speciality", None)) for slot in slots)
            
        functional_output_slots = output_slots if not triggered else delayed_output_slots
        functional_special_output_slots = special_output_slots if not triggered else delayed_special_output_slots
        functional_special_output_slots = extract_special_outputs(functional_special_output_slots) # convert into key value pair dict
        
        source_connections = node.get("source_connections", [])
        
        for connection in source_connections:
            target_node_id = connection.get("target", None)
            target_slot = connection.get("target_slot", None)
            source_slot = connection.get("source_slot", None)
            output_present = False
            if source_slot in functional_special_output_slots.keys():
                functional_special_output_fn = speciality_output.get(functional_special_output_slots.get(source_slot), lambda : None)
                output = functional_special_output_fn()
                output_present =True
            elif source_slot in functional_output_slots:
                output = outputs.get(source_slot, None)
                output_present = True
                
            if output_present:
                with node_dict_lock:
                    nodes_dict.get(target_node_id).setdefault("inputs", {}).update({target_slot: output})
                children.append(target_node_id)
                
        with node_dict_lock:
            nodes_dict.get(node_id).update({"executed": True})
        
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
