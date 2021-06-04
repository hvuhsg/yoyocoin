from p2pnetwork.node import Node


BROADCAST_MAX_TTL = 10


class BlockchainNode(Node):
    def __init__(self, new_block_callback, new_transaction_callback, host="0.0.0.0", port=2424, debug=False):
        self.domains = []
        self.peers_address = []
        self.new_block_callback = new_block_callback
        self.new_transaction_callback = new_transaction_callback
        self._last_message = None
        super().__init__(host, port)
        self.debug = debug

    def get_last_message(self):
        return self._last_message

    def get_peers_from_dns(self):
        pass

    def connect_to_network(self):
        if len(self.peers_address) == 0:
            self.get_peers_from_dns()
        for peer_host, peer_port in self.peers_address:
            if peer_host == self.host:
                continue  # do not connect to you'r self
            self.connect_with_node(host=peer_host, port=peer_port)

    def process_message(self, data):
        if data.get("route", None) == "/new_block":
            self.new_block_callback(data["block"])
        elif data.get("route", None) == "/new_transaction":
            self.new_transaction_callback(data["transaction"])
        if self.debug:
            self._last_message = data

    def node_message(self, node, data):
        if data.get("type", None) == "broadcast" and BROADCAST_MAX_TTL >= data["ttl"] > 0:
            data["ttl"] -= 1
            self.send_to_nodes(data, exclude=[node])
        self.process_message(data)
        print("node_message from " + node.id + ": " + str(data))

    def send_broadcast(self, data: dict):
        data["type"] = "broadcast"
        data["ttl"] = BROADCAST_MAX_TTL
        self.send_to_nodes(data)
        print("send broadcast", data)

    def forge_block(self, block):
        route = "/new_block"
        data = {"block": block, "route": route}
        self.send_broadcast(data)
