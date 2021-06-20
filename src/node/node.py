from p2pnetwork.node import Node

from .message import Message, Route


class BlockchainNode(Node):
    def __init__(
        self,
        new_block_callback,
        new_transaction_callback,
        host="0.0.0.0",
        port=2424,
        debug=False,
        message_memory_max_size=30,
    ):
        self.domains = []
        self.peers_address = [("127.0.0.1", 12345)]
        self.new_block_callback = new_block_callback
        self.new_transaction_callback = new_transaction_callback
        self._last_message = None
        self._messages_hash_memory = []
        self._messages_hash_memory_max_size = message_memory_max_size
        super().__init__(host, port)
        self.debug = debug
        self.connect_to_network()

    def get_last_message(self) -> Message:
        return self._last_message

    def get_peers_from_dns(self):
        pass

    def save_for_relay_detection(self, message: Message):
        self._messages_hash_memory.append(message.hash)
        if len(self._messages_hash_memory) > self._messages_hash_memory_max_size:
            self._messages_hash_memory.pop(0)

    def is_broadcast_relay(self, message: Message) -> bool:
        return message.hash in self._messages_hash_memory

    def connect_to_network(self):
        if len(self.peers_address) == 0:
            self.get_peers_from_dns()
        for peer_host, peer_port in self.peers_address:
            if (peer_host, peer_port) == (self.host, self.port):
                continue  # do not connect to you'r self
            self.connect_with_node(host=peer_host, port=peer_port)

    def process_message(self, message: Message):
        if message.route == Route.NewBlock:
            self.new_block_callback(message.payload)
        elif message.route == Route.NewTX:
            self.new_transaction_callback(message.payload)

        if self.debug:
            self._last_message = message

    def node_message(self, node, data):
        message = Message.from_dict(data)
        if message.broadcast_forward() and not self.is_broadcast_relay(message):
            self.save_for_relay_detection(message)
            self.send_to_nodes(message.to_dict(), exclude=[node])
        self.process_message(message)

    def send(self, message: Message):
        data = message.to_dict()
        self.send_to_nodes(data)

