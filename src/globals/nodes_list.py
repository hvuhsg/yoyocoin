from random import choice
from .singleton import Singleton


class NodesList(Singleton):
    def __init__(self):
        self._nodes = {}  # {address: dict<node data>}
        super().__init__()

    def add_node(self, address):
        if address in self._nodes:
            return
        self._nodes[address] = {}

    def add_multiple_nodes(self, nodes):
        self._nodes.update({node: {} for node in nodes})

    def get_multiple_nodes(self, count: int) -> list:
        count = min(self.count(), count)
        return list(self._nodes.keys())[:count]

    def count(self):
        return len(self._nodes)

    def get_random_node(self):
        return choice(list(self._nodes.keys()))


def get_nodes_list() -> NodesList:
    return NodesList.get_instance()
