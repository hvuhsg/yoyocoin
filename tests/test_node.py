import unittest
from time import sleep
from random import randrange

from src.node import BlockchainNode, Message, MessageFactory


class NodeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.message_factory = MessageFactory("public", "private")
        self.node1 = BlockchainNode(
            None, None, host="127.0.0.1", port=randrange(1024, 65000), debug=True
        )
        self.node2 = BlockchainNode(
            None, None, host="127.0.0.2", port=randrange(1024, 65000), debug=True
        )
        self.node3 = BlockchainNode(
            None, None, host="127.0.0.3", port=randrange(1024, 65000), debug=True
        )
        self.node1.start()
        self.node2.start()
        self.node3.start()

    def tearDown(self) -> None:
        self.node1.stop()
        self.node2.stop()
        self.node3.stop()

    def connect_all(self):
        nodes = [self.node1, self.node2, self.node3]
        for n in nodes:
            for n2 in nodes:
                if n.host != n2.host:
                    n.connect_with_node(n2.host, n2.port)

    def one_way_connection(self, n1: BlockchainNode, n2: BlockchainNode):
        n1.connect_with_node(n2.host, n2.port)


class TestDataTransfer(NodeTestCase):
    def test_one_way_data_transfer(self):
        self.one_way_connection(self.node1, self.node2)
        data = {"test": True}
        message = self.message_factory.test_direct(data)
        self.node1.send(message)

        sleep(0.5)
        assert self.node2.get_last_message().payload == data


class TestBroadcast(NodeTestCase):
    def test_broadcast_message_transfer(self):
        self.one_way_connection(self.node1, self.node2)
        self.one_way_connection(self.node2, self.node3)

        data = {"test": "broadcast test"}
        message = self.message_factory.test_broadcast(data)
        self.node1.send(message)

        sleep(0.5)
        assert self.node3.get_last_message().payload == data

    def test_circular_broadcast(self):
        self.one_way_connection(self.node1, self.node2)
        self.one_way_connection(self.node2, self.node3)
        self.one_way_connection(self.node3, self.node2)

        data = {"test": "broadcast test 2"}
        message = self.message_factory.test_broadcast(data)
        self.node1.send(message)

        sleep(0.5)
        assert self.node3.get_last_message().payload == data
