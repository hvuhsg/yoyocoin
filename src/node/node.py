from p2pnetwork.node import Node


class BlockchainNode(Node):
    def __init__(self):
        super().__init__("0.0.0.0", 2424)

    def node_message(self, node, data):
        print("node_message from " + node.id + ": " + str(data))
