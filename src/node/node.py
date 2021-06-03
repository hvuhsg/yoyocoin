from p2pnetwork.node import Node


class BlockchainNode(Node):
    def __init__(self):
        self.domains = []
        self.peers_address = []
        super().__init__("0.0.0.0", 2424)

    def connect_to_network(self):
        pass

    def process_message(self):
        pass

    def node_message(self, node, data):
        if data.get("type", None) == "broadcast" and data["ttl"] > 0:
            data["ttl"] -= 1
            self.send_to_nodes(data, exclude=[node])
            self.process_message()
        print("node_message from " + node.id + ": " + str(data))
