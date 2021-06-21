from threading import Timer
from pprint import pprint
from time import sleep

from ecdsa import SigningKey
from base64 import b64encode

from storage import Storage
from node import BlockchainNode, MessageFactory
from blockchain import Blockchain, Block, Transaction
from protocol.protocol import Protocol


class Manager:
    def __init__(self):
        self.storage = Storage(filename="json.db")
        self.blockchain = Blockchain(pruned=False, is_test_net=True)

        self.private_key = SigningKey.generate()
        self.public_key = self.private_key.get_verifying_key()
        self.public_address = b64encode(self.public_key.to_string()).decode()
        self.private_address = b64encode(self.private_key.to_string()).decode()
        self.nonce = 0

        self.message_factory = MessageFactory(
            node_pub_address=self.public_address,
            node_pri_address=self.private_address,
        )

        self.public_address_recipient = b64encode(
            SigningKey.generate().get_verifying_key().to_string()
        ).decode()
        # For testing , TODO: remove in prod

        self.protocol = Protocol(self.blockchain)
        self.node = BlockchainNode(
            chain_score_request_callback=self.protocol.chain_info,
            chain_blocks_request_callback=self.protocol.chain_blocks,
            new_block_callback=self.protocol.new_block,
            new_transaction_callback=self.protocol.new_transaction,
            host="127.0.0.1",
            port=int(input("Enter port: ")),
        )

    def create_transaction(self, to=None, amount=5, fee=1):
        if to is None:
            to = self.public_address_recipient
        transaction = self.blockchain.new_transaction(
            sender=self.public_address,
            recipient=to,
            amount=amount,
            fee=fee,
            nonce=self.nonce,
            sender_private_addr=self.private_address,
        )
        self.nonce += 1
        message = self.message_factory.new_transaction(transaction.to_dict())
        self.node.send(message)

    def create_block(self):
        block = self.blockchain.new_block(
            forger=self.public_address,
            forger_private_addr=self.private_address,
        )
        self.protocol.check_block_score(block)
        message = self.message_factory.new_block(block.to_dict())
        self.node.send(message)

    def new_tx_every_x_seconds(self, x: int):
        t = Timer(x, self.new_tx_every_x_seconds, [x])
        t.daemon = True
        t.start()
        self.create_transaction()

    def new_block_every_x_seconds(self, x: int):
        self.protocol.insert_new_blocks()
        sleep(10)
        t = Timer(x, self.new_block_every_x_seconds, [x])
        t.daemon = True
        t.start()
        self.create_block()

    def run(self):
        self.node.start()
        sleep(15)
        self.new_tx_every_x_seconds(15)
        self.new_block_every_x_seconds(20)
        sleep(200)


if __name__ == "__main__":
    manager = Manager()
    try:
        manager.run()
    except KeyboardInterrupt:
        print("Stopping... plz wait.")
        manager.node.stop()
    for b in manager.blockchain.chain:
        for tx in b.transactions:
            pprint(tx.to_dict())
