from typing import Tuple
from time import sleep
import argparse
import sys

from loguru import logger

import api
import config
from wallet import Wallet
from blockchain import Blockchain, Transaction, Block
from scheduler import Scheduler
from network import Node, messages
from chain_extender import ChainExtender


from network.network_handlers.on_chain_info_request import ChainInfoRequestHandler
from network.network_handlers.on_chain_info import ChainInfoHandler
from network.network_handlers.on_new_block import NewBlockHandler
from network.network_handlers.on_new_transaction import NewTransactionHandler
from network.network_handlers.on_transactions_request import TransactionsRequestHandler
from network.network_handlers.on_transactions_response import TransactionsHandler


def setup_wallet() -> Wallet:
    secret = 'test-key'  # input("Enter wallet secret: ")
    if not secret:
        secret = None
    wallet = Wallet(secret_passcode=secret)
    Wallet.set_main_wallet(wallet)
    return wallet


def setup_blockchain() -> Blockchain:
    #  TODO: load from disk
    blockchain = Blockchain(pruned=not config.IS_FULL_NODE, is_test_net=config.IS_TEST_NET)
    Blockchain.set_main_chain(blockchain)
    return blockchain


def setup_node() -> Tuple[Node, ChainExtender]:
    node = Node(is_full_node=config.IS_TEST_NET)

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


def setup_api():
    api.run()


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
        func=chain_extender.publish_new_transaction,
        name="add new transaction",
        interval=60,
        sync=False,
        run_thread=True
    )


def test(node, blockchain, wallet):
    messages.SyncRequest(score=0, length=0).send(node)
    new_block = blockchain.new_block(wallet.public_address, wallet.private_address)
    blockchain.add_block(new_block)
    block = blockchain.chain[0]
    messages.NewBlock(block=block.to_dict(), privies_hash=block.previous_hash, index=block.index).send(node)

    transaction = Transaction(sender=wallet.public_address, recipient=wallet.public_address, amount=10, nonce=50)
    transaction.create_signature(wallet.private_address)
    messages.NewTransaction(
        transaction=transaction.to_dict(),
        hash=transaction.hash(),
        nonce=transaction.nonce
    ).send(node)

    # TODO: Add TransactionsRequest message messages.TransactionsRequest
    node.publish_to_topic("transactions-request")


def create_genesis(developer_secret: str):
    wallet = Wallet(secret_passcode=developer_secret)
    print("GENESIS_WALLET_ADDRESS:", wallet.public)

    g_transaction = Transaction(sender="0", recipient=wallet.public, amount=1000000000000, nonce=0, fee=0)
    signature = g_transaction.sign(wallet.private_key)
    g_transaction.signature = signature

    g_block = Block(forger=wallet.public, index=0, previous_hash="0", transactions=[g_transaction])
    g_block.create_signature(wallet.private)
    print(g_block.to_dict())
    return g_block


def override_config():
    parser = argparse.ArgumentParser(description='Yoyocoin node daemon')
    parser.add_argument('--expose-api', action="store_true", help='Expose http api for this node')
    parser.add_argument('--api-port', type=int, help='Port for the node external api (http)')
    parser.add_argument('--api-host', type=str, help='Host for the node external api (http)')
    parser.add_argument('--ipfs-port', type=int, help='IPFS daemon port')
    parser.add_argument("--test-net", "-t", action="store_true", help="Run node with test net configuration")
    parser.add_argument("--prune-node", "-p", action="store_true", help="Only save blockchain summery")
    args = vars(parser.parse_args())

    if args["api_port"] is not None:
        config.API_PORT = args["api_port"]
    if args["api_host"] is not None:
        config.API_HOST = args["api_host"]
    if args["ipfs_port"] is not None:
        config.IPFS_PORT = args["ipfs_port"]
    config.IS_TEST_NET = args["test_net"]
    config.IS_FULL_NODE = not args["prune_node"]
    config.EXPOSE_API = args["expose_api"]


def idle():
    try:
        while True:
            sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass


def main():
    override_config()

    logger.remove()
    logger.add(sys.stdout, level="INFO")

    # 1
    wallet = setup_wallet()

    # 2
    scheduler = Scheduler(min_time_step=config.SCHEDULER_STEP_LENGTH)

    # 3
    blockchain = setup_blockchain()

    # 4
    node, chain_extender = setup_node()

    # 5
    messages.SyncRequest(score=blockchain.score, length=blockchain.length).send(node)

    # 6
    register_scheduler_jobs(scheduler, chain_extender)
    scheduler.start()

    # 7
    if config.EXPOSE_API:
        setup_api()

    idle()

    # Stopping
    scheduler.stop()
    # TODO: close storage

    # test
    # print("run tests")
    # test(node, blockchain, wallet)


if __name__ == "__main__":
    if config.ENV_TYPE == "PRODUCTION":
        logger.info("Waiting for the IPFS node to initialize.")
        sleep(10)
    main()
