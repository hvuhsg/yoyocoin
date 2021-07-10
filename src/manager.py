from config import PORT, TEST_NET
from wallet import Wallet
from blockchain import Blockchain
from scheduler import Scheduler
from protocols import GossipTransactionsProtocol, LotteryProtocol
from node import Node


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


def setup_node() -> Node:
    node = Node(host="127.0.0.1", port=PORT, max_outbound_connections=10, max_inbound_connections=10)
    node.register_protocol(GossipTransactionsProtocol())
    node.register_protocol(LotteryProtocol())
    return node


def main():
    setup_wallet()

    scheduler = Scheduler(min_time_step=1)
    scheduler.daemon = True

    node = setup_node()
    setup_blockchain()

    scheduler.start()
    node.run()  # IDLE

if __name__ == "__main__":
    main()
