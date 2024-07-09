from v2.node_manager import NodeManager

from v2.executors.datanode import DataNode
from v2.executors.function_node import FunctionNode
from v2.executors.foreach_node import ForEachNode
from v2.executors.conditional_node import ConditionalNode
from v2.executors.input_node import InputNode
from v2.executors.output_node import OutputNode
from v2.executors.flow_node import FlowNode


def register_executors():
    NodeManager.register("DataNode", DataNode)
    NodeManager.register("FunctionNode", FunctionNode)
    NodeManager.register("ForEachNode", ForEachNode)
    NodeManager.register("ConditionalNode", ConditionalNode)
    NodeManager.register("InputNode", InputNode)
    NodeManager.register("OutputNode", OutputNode)
    NodeManager.register("FlowNode", FlowNode)
