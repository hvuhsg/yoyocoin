from typing import Tuple

from loguru import logger

from blockchain import Blockchain, Block
from blockchain.exceptions import NonSequentialBlockIndexError, NonMatchingHashError
from network import Node, messages
from wallet import Wallet


class ChainExtender:
    def __init__(self, node: Node):
        self.node = node

        self.best_block: Block = None
        self.best_block_score = 0

        self._sender = Wallet()
        self._recipient = Wallet()

    @property
    def _blockchain(self) -> Blockchain:
        return Blockchain.get_main_chain()

    @property
    def _wallet(self) -> Wallet:
        return Wallet.get_main_wallet()

    def _reset(self):
        self.best_block = None
        self.best_block_score = 0

    def _publish_my_block(self, my_block: Block):
        messages.NewBlock(
            block=my_block.to_dict(),
            privies_hash=my_block.previous_hash,
            index=my_block.index,
        ).send(self.node)

    def _get_chain_info(self) -> Tuple[dict, dict]:
        """
        Return blockchain block hashes
        :return: tuple of chain info (block hashes) and chain summery (chain length and score)
        """
        blockchain: Blockchain = Blockchain.get_main_chain()
        blocks = blockchain.chain
        score = blockchain.score
        length = blockchain.length
        return {"blocks": blocks}, {"score": score, "length": length}

    def publish_new_transaction(self):
        # TODO: remove! just for testing
        new_transaction = self._blockchain.new_transaction(
            sender=self._sender.public_address,
            recipient=self._recipient.public_address,
            amount=10,
            nonce=self._sender.nonce,
        )
        signature = self._sender.sign(new_transaction.hash())
        new_transaction.signature = signature
        self._blockchain.add_transaction(new_transaction)
        messages.NewTransaction(
            transaction=new_transaction.to_dict(),
            hash=new_transaction.hash(),
            nonce=new_transaction.nonce,
        ).send(self.node)

    def _publish_chain_info_request(self):
        messages.SyncRequest(
            score=self._blockchain.score, length=self._blockchain.length
        ).send(self.node)

    def create_my_own_block(self):
        my_block = self._blockchain.new_block(forger=self._wallet.public_address)
        signature = self._wallet.sign(my_block.hash())
        my_block.signature = signature
        if self.check_block(my_block):
            self._publish_my_block(my_block=my_block)
            logger.debug("Block is created and published")

    def add_best_block_to_chain(self):
        if self.best_block is None:
            return
        try:
            self._blockchain.add_block(block=self.best_block)
            logger.success(
                f"Block index [{self.best_block.index}] added to chain - {self.best_block.hash()}"
                f" tx: {len(self.best_block.transactions)}"
            )
        except NonSequentialBlockIndexError:
            self._publish_chain_info_request()
        finally:
            self._reset()

    def check_block(self, block: Block):
        try:
            self._blockchain.validate_block(block)
        except NonSequentialBlockIndexError:
            if block.index > self._blockchain.length:
                self._publish_chain_info_request()
        except NonMatchingHashError:
            self._publish_chain_info_request()
        new_block_score = self._blockchain.get_block_score(block)
        if new_block_score > self.best_block_score:
            self.best_block = block
            self.best_block_score = new_block_score
            return True
        return False
