from config import PORT, TEST_NET
from wallet import Wallet
from blockchain import Blockchain
from scheduler import Scheduler
from ipfs import Node
from network_handlers.on_chain_info_request import ChainInfoRequestHandler


def setup_wallet():
    secret = input("Enter wallet secret: ")
    if not secret:
        secret = None
    wallet = Wallet(secret_passcode=secret)
    Wallet.set_main_wallet(wallet)


def setup_blockchain():
    #  todo: load from disk
    blockchain = Blockchain(pruned=False, is_test_net=TEST_NET)
    Blockchain.set_main_chain(blockchain)
    #  todo: sync chain


def setup_node():
    callback = lambda x: print(x)
    node = Node(callback, callback, callback, callback, callback, is_full_node=True)
    chain_info_request_handler = ChainInfoRequestHandler(node)
    node.add_listener(chain_info_request_handler)
    node.request_chain_info()


def main():
    setup_wallet()

    scheduler = Scheduler(min_time_step=1)
    scheduler.daemon = True

    setup_blockchain()


if __name__ == "__main__":
    main()
