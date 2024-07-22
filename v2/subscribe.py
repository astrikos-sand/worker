from v2.node_manager import NodeManager

from v2.executors.datanode import DataNode
from v2.executors.function_node import FunctionNode
from v2.executors.foreach_node import ForEachNode
from v2.executors.conditional_node import ConditionalNode
from v2.executors.flow_node import FlowNode, InputNode, OutputNode
from v2.executors.block_node import BlockNode


def register_executors():
    NodeManager.register("DataNode", DataNode)
    NodeManager.register("FunctionNode", FunctionNode)
    NodeManager.register("ForEachNode", ForEachNode)
    NodeManager.register("ConditionalNode", ConditionalNode)
    NodeManager.register("InputNode", InputNode)
    NodeManager.register("OutputNode", OutputNode)
    NodeManager.register("FlowNode", FlowNode)
    NodeManager.register("BlockNode", BlockNode)
