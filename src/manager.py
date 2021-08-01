from typing import Tuple
from time import sleep
import sys

from loguru import logger

from config import IS_TEST_NET, IS_FULL_NODE, SCHEDULER_STEP_LENGTH
from wallet import Wallet
from blockchain import Blockchain, Transaction
from scheduler import Scheduler
from ipfs import Node, Message
from chain_extender import ChainExtender

from network_handlers.on_chain_info_request import ChainInfoRequestHandler
from network_handlers.on_chain_info import ChainInfoHandler
from network_handlers.on_new_block import NewBlockHandler
from network_handlers.on_new_transaction import NewTransactionHandler
from network_handlers.on_transactions_request import TransactionsRequestHandler
from network_handlers.on_transactions_response import TransactionsHandler


def setup_wallet() -> Wallet:
    secret = input("Enter wallet secret: ")
    if not secret:
        secret = None
    wallet = Wallet(secret_passcode=secret)
    Wallet.set_main_wallet(wallet)
    return wallet


def setup_blockchain() -> Blockchain:
    #  TODO: load from disk
    blockchain = Blockchain(pruned=not IS_FULL_NODE, is_test_net=IS_TEST_NET)
    Blockchain.set_main_chain(blockchain)
    return blockchain


def setup_node() -> Tuple[Node, ChainExtender]:
    node = Node(is_full_node=IS_FULL_NODE)

    chain_extender = ChainExtender(node)

    chain_info_request_handler = ChainInfoRequestHandler(node)
    chain_info_handler = ChainInfoHandler(node)
    new_block_handler = NewBlockHandler(node, on_new_block=chain_extender.check_block)
    new_transaction_handler = NewTransactionHandler(node)
    transactions_request_handler = TransactionsRequestHandler(node)
    transactions_handler = TransactionsHandler(node)

    node.add_listener(chain_info_request_handler)
    node.add_listener(chain_info_handler)
    node.add_listener(new_block_handler)
    node.add_listener(new_transaction_handler)
    node.add_listener(transactions_request_handler)
    node.add_listener(transactions_handler)

    return node, chain_extender


def register_scheduler_jobs(scheduler: Scheduler, chain_extender: ChainExtender):
    scheduler.add_job(
        func=chain_extender.add_best_block_to_chain,
        name="new block every 2 minutes",
        interval=60 * 2,
        sync=True,
        run_thread=True
    )
    scheduler.add_job(
        func=chain_extender.create_my_own_block,
        name="create my block",
        interval=60 * 1.5,
        sync=False,
        run_thread=True
    )
    scheduler.add_job(
        func=chain_extender.publish_chain_info,
        name="publish my chain info",
        interval=60 * 2.6,
        sync=False,
        run_thread=True
    )
    scheduler.add_job(
        func=chain_extender.publish_new_transaction,
        name="add new transaction",
        interval=60,
        sync=False,
        run_thread=True
    )


def test(node, blockchain, wallet):
    node.publish_to_topic("chain-request", message=Message(meta={"score": 0}))
    new_block = blockchain.new_block(wallet.public_address, wallet.private_address)
    blockchain.add_block(new_block)
    block = blockchain.chain[0]
    node.publish_to_topic(
        "new-block",
        message=Message(
            meta={"hash": block.hash(), "index": block.index},
            cid=node.create_cid(data=block.to_dict())
        )
    )

    transaction = Transaction(sender=wallet.public_address, recipient=wallet.public_address, amount=10, nonce=50)
    transaction.create_signature(wallet.private_address)
    node.publish_to_topic(
        "new-transaction",
        message=Message(
            meta={"hash": transaction.hash(), "nonce": transaction.nonce},
            cid=node.create_cid(data=transaction.to_dict())
        )
    )

    node.publish_to_topic("transactions-request")


def idle():
    try:
        while True:
            sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass


def main():
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    # 1
    wallet = setup_wallet()

    # 2
    scheduler = Scheduler(min_time_step=SCHEDULER_STEP_LENGTH)

    # 3
    blockchain = setup_blockchain()

    # 4
    node, chain_extender = setup_node()

    # 5
    node.publish_to_topic("chain-request", message=Message(meta={"score": 0}))

    # 6
    register_scheduler_jobs(scheduler, chain_extender)
    scheduler.start()

    idle()

    # Stopping
    scheduler.stop()
    # TODO: close storage

    # test
    # print("run tests")
    # test(node, blockchain, wallet)

if __name__ == "__main__":
    main()
