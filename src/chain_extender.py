from typing import Tuple

from loguru import logger

from blockchain import Blockchain, Block
from blockchain.exceptions import NonSequentialBlockIndexError, NonMatchingHashError
from network import Node, messages
from wallet import Wallet
from scheduler import Scheduler
from event_stream import EventStream, Event, OneTimeListener, Listener


class GlobalLoopHandler:
    def __init__(self):
        self.best_block: Block = None
        self.best_block_score = 0

        self._sender = Wallet()
        self._recipient = Wallet()

    @property
    def node(self) -> Node:
        return Node.get_instance()

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

        event_stream: EventStream = EventStream()
        event_stream.publish(
            topic="new-transaction",
            event=Event(name="test-new-transaction", transaction=new_transaction)
        )

        # TODO: send on new-transaction event
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
            event_stream: EventStream = EventStream.get_instance()
            event_stream.publish("new-block", Event(name="time-to-add-lottery-winning-block", block=self.best_block))
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

    def on_network_block(self, event: Event):
        self.check_block(event.args["block"])


def send_sync_request(event):
    if event.name != "end-setup":
        return False
    blockchain = Blockchain.get_main_chain()
    node = Node.get_instance()
    messages.SyncRequest(score=blockchain.score, length=blockchain.length).send(node)
    return True  # Stop the listener


def setup_global_loop_handler():
    scheduler = Scheduler.get_instance()
    chain_extender = GlobalLoopHandler()

    send_sync_request_when_setup_end = OneTimeListener(topic="lifecycle", callback=send_sync_request)
    send_sync_request_when_setup_end.start()

    check_blocks_sent_by_network = Listener(topic="new-block-from-network", callback=chain_extender.on_network_block)
    check_blocks_sent_by_network.start()

    scheduler.add_job(
        func=chain_extender.add_best_block_to_chain,
        name="new block every 2 minutes",
        interval=60 * 2,
        sync=True,
        run_thread=True,
    )
    scheduler.add_job(
        func=chain_extender.create_my_own_block,
        name="create my block",
        interval=60 * 1.5,
        sync=False,
        run_thread=True,
    )
    scheduler.add_job(
        func=chain_extender.publish_new_transaction,
        name="add new transaction",
        interval=60,
        sync=False,
        run_thread=True,
    )
