from enum import auto

from node.blueprints.message import Message
from node.blueprints.protocol import Protocol
from ..nodes_list import get_nodes_list


class Routes:
    Publish = auto()
    RequestList = auto()
    ResponseList = auto()


class NodesListProtocol(Protocol):
    name: str = "nodes_list"

    def process(self, message: Message) -> dict:
        nodes_list = get_nodes_list()
        if Routes(message.route) == Routes.Publish:
            if "address" not in message.params:
                return {"Error": "address is required"}
            nodes_list.add_node(message.params["address"])
        elif Routes(message.route) == Routes.RequestList:
            if "count" in message.params:
                count = message.params["count"]
            else:
                count = 100
            return self.response_list(nodes_list, count)
        elif Routes(message.route) == Routes.ResponseList:
            if "nodes" not in message.params:
                return {"Error": "nodes is required"}
            nodes_list.add_multiple_nodes(message.params["nodes"])
        else:
            return {"Error": "route is not found"}

    @classmethod
    def publish(cls, address):
        return {"protocol": cls.name, "route": Routes.Publish.value, "params": {"address": address}}

    @classmethod
    def request_list(cls, count: int):
        return {"protocol": cls.name, "route": Routes.RequestList.value, "params": {"count": count}}

    @classmethod
    def response_list(cls, nodes_list, count: int):
        return {
            "protocol": cls.name,
            "route": Routes.ResponseList.value,
            "nodes": nodes_list.get_multiple_nodes(count)
        }
