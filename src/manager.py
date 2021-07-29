from config import IS_TEST_NET, IS_FULL_NODE, SCHEDULER_STEP_LENGTH
from wallet import Wallet
from blockchain import Blockchain, Transaction
from scheduler import Scheduler
from ipfs import Node, Message

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
    blockchain = Blockchain(pruned=~IS_FULL_NODE, is_test_net=IS_TEST_NET)
    Blockchain.set_main_chain(blockchain)
    return blockchain


def setup_node() -> Node:
    node = Node(is_full_node=IS_FULL_NODE)

    chain_info_request_handler = ChainInfoRequestHandler(node)
    chain_info_handler = ChainInfoHandler(node)
    new_block_handler = NewBlockHandler(node)
    new_transaction_handler = NewTransactionHandler(node)
    transactions_request_handler = TransactionsRequestHandler(node)
    transactions_handler = TransactionsHandler(node)

    node.add_listener(chain_info_request_handler)
    node.add_listener(chain_info_handler)
    node.add_listener(new_block_handler)
    node.add_listener(new_transaction_handler)
    node.add_listener(transactions_request_handler)
    node.add_listener(transactions_handler)

    return node


def main():
    # 1
    wallet = setup_wallet()

    # 2
    scheduler = Scheduler(min_time_step=SCHEDULER_STEP_LENGTH)
    # TODO: create - block creator

    # 3
    blockchain = setup_blockchain()

    # 4
    node = setup_node()

    # test
    node.publish_to_topic("chain-request", message=Message(meta={"score": 0}))
    new_block = blockchain.new_block(wallet.public_address, wallet.private_address)
    # blockchain.add_block(new_block)
    # block = blockchain.chain[0]
    # node.publish_to_topic(
    #     "new-block",
    #     message=Message(
    #         meta={"hash": block.hash(), "index": block.index},
    #         cid=node.create_cid(data=block.to_dict())
    #     )
    # )
    #
    # transaction = Transaction(sender=wallet.public_address, recipient=wallet.public_address, amount=10, nonce=50)
    # transaction.create_signature(wallet.private_address)
    # node.publish_to_topic(
    #     "new-transaction",
    #     message=Message(
    #         meta={"hash": transaction.hash(), "nonce": transaction.nonce},
    #         cid=node.create_cid(data=transaction.to_dict())
    #     )
    # )
    #
    # node.publish_to_topic("transactions-request")

    # 5
    #  TODO: sync chain


if __name__ == "__main__":
    main()
