from typing import Tuple, Set
from random import choice

from .client import Client

NodeAddress = Tuple[str, int]  # ("123.123.123.123", 8564)
NodeIP = str

KNOWN_NODES = [("127.0.0.1", 12345)]


class NetworkManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise ValueError("Initiate NetworkManager first")
        return cls._instance

    def __init__(self, max_outbound_connection: int, max_node_list: int, port: int):
        self.max_outbound_connection = max_outbound_connection
        self.outbound_connections: Set[NodeAddress] = set()
        self.max_node_list = max_node_list
        self.nodes_list: Set[NodeAddress] = set(KNOWN_NODES)
        self.port = port

        self.__class__._instance = self  # Initialize Singleton

    def setup(self):
        self.get_initial_nodes()
        self.make_outbound_connections()

    def outbound_connections_is_full(self) -> bool:
        return len(self.outbound_connections) >= self.max_outbound_connection

    def make_outbound_connections(self):
        nodes = self.choose_outbound_connections()
        for node in nodes:
            self.connect_to_node(node)

    def get_initial_nodes(self):
        for node in KNOWN_NODES:
            address = self.url_from_address(node)
            nodes_list = Client.get_nodes_list(address)
            if nodes_list:
                for n in nodes_list:
                    n = tuple(n)
                    self.add_to_node_list(n)

    def choose_outbound_connections(self):
        nodes = []
        list_nodes = list(self.nodes_list)
        for _ in range(min(len(list_nodes), self.max_outbound_connection - len(self.outbound_connections))):
            nodes.append(choice(list_nodes))
        return nodes

    def connect_to_node(self, address: NodeAddress):
        url = self.url_from_address(address)
        if self.can_add_outbound_connection(address):
            if Client.connect_to_node(url):
                print("Connected to", address)
                self.add_outbound_connection(address)

    def add_outbound_connection(self, address: NodeAddress):
        if self.can_add_outbound_connection(address):
            self.outbound_connections.add(address)

    def can_add_outbound_connection(self, address: NodeAddress) -> bool:
        if address[1] == self.port:
            return False  # TODO: remove on prod for non self connection and testing
        if address not in self.outbound_connections and len(self.outbound_connections) < self.max_outbound_connection:
            return True
        return False

    def add_to_node_list(self, address: NodeAddress):
        self.nodes_list.add(address)
        if len(self.nodes_list) > self.max_node_list:
            self.nodes_list.remove(choice(list(self.nodes_list)))

    def broadcast_address(self, address: NodeAddress):
        for node in self.outbound_connections.copy():
            url = self.url_from_address(node)
            Client.send_address(url, address[0], address[1])

    def broadcast_best_lottery_block(self, block):
        for node in self.outbound_connections.copy():
            url = self.url_from_address(node)
            Client.send_best_lottery_block(url, block.to_dict())

    @staticmethod
    def url_from_address(address: NodeAddress):
        return f"http://{address[0]}:{address[1]}"

