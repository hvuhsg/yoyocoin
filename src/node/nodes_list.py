from random import shuffle

from globals.singleton import Singleton


class NodesList(Singleton):
    def __init__(self):
        # todo: load from storage
        self._nodes = {("127.0.0.1", 12345): {}}  # {address: dict<node data>}
        super().__init__()

    def count(self) -> int:
        return len(self._nodes)

    def _initial_nodes_list(self):
        #  todo: get first nodes from dns
        pass

    def add_node(self, address: list):
        address = tuple(address)
        if address in self._nodes:
            return
        self._nodes[address] = {}

    def add_multiple_nodes(self, nodes):
        self._nodes.update({tuple(node): {} for node in nodes})

    def get_random_nodes(self, count: int):
        nodes = list(self._nodes.keys()).copy()
        shuffle(nodes)
        return nodes[:min(len(self._nodes), count)]


def get_nodes_list() -> NodesList:
    return NodesList.get_instance()
