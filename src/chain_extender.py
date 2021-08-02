from typing import Tuple

from loguru import logger

from blockchain import Blockchain, Block
from blockchain.exceptions import NonSequentialBlockIndexError
from ipfs import Node, Message
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
        block_cid = self.node.create_cid(data=my_block.to_dict())
        self.node.publish_to_topic(
            "new-block",
            message=Message(
                cid=block_cid,
                meta={"p_hash": my_block.previous_hash, "index": my_block.index}
            )
        )

    def _get_chain_info(self) -> Tuple[dict, dict]:
        """
        Return blockchain block hashes
        :return: tuple of chain info (block hashes) and chain summery (chain length and score)
        """
        blockchain: Blockchain = Blockchain.get_main_chain()
        blocks = blockchain.chain
        score = blockchain.state.score
        length = blockchain.state.length
        return {"blocks": blocks}, {"score": score, "length": length}

    def publish_new_transaction(self):
        # TODO: remove! just for testing
        new_transaction = self._blockchain.new_transaction(
            sender=self._sender.public_address,
            recipient=self._recipient.public_address,
            amount=10,
            nonce=self._sender.nonce,
            sender_private_addr=self._sender.private_address
        )
        cid = self.node.create_cid(new_transaction.to_dict())
        self.node.publish_to_topic(
            "new-transaction",
            message=Message(cid=cid, meta={"hash": new_transaction.hash(), "nonce": new_transaction.nonce})
        )

    def publish_chain_info(self):
        # TODO: remove this hack
        chain_info, summery = self._get_chain_info()
        blocks_cids = []
        blocks_hashes = []
        for block in chain_info["blocks"]:
            block_dict = block.to_dict()
            blocks_cids.append(self.node.create_cid(block_dict))
            blocks_hashes.append(block.hash())
        cid = self.node.create_cid(
            {"blocks_cid": blocks_cids, "blocks_hash": blocks_hashes}
        )
        self.node.publish_to_topic(
            topic='chain-response', message=Message(cid=cid, meta=summery)
        )

    def _publish_chain_info_request(self):
        self.node.publish_to_topic(
            "chain-request",
            message=Message(meta={"score": self._blockchain.state.score})
        )

    def create_my_own_block(self):
        my_block = self._blockchain.new_block(
            forger=self._wallet.public_address, forger_private_addr=self._wallet.private_address
        )
        my_block_score = self._blockchain.get_block_score(my_block)
        if my_block_score > self.best_block_score:
            self.check_block(my_block)
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
            if block.index > self._blockchain.state.length:
                self._publish_chain_info_request()
        new_block_score = self._blockchain.get_block_score(block)
        if new_block_score > self.best_block_score:
            self.best_block = block
            self.best_block_score = new_block_score
