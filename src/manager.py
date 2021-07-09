import uvicorn

from config import PORT, TEST_NET
from wallet import Wallet
from blockchain import Blockchain
from scheduler import Scheduler


def setup():
    secret = input("Enter wallet secret: ")
    if not secret:
        secret = None
    wallet = Wallet(secret_passcode=secret)
    Wallet.set_main_wallet(wallet)

    blockchain = Blockchain(pruned=False, is_test_net=TEST_NET)
    Blockchain.set_main_chain(blockchain)

    scheduler = Scheduler(min_time_step=1)
    scheduler.daemon = True
    scheduler.start()


def main():
    setup()
    uvicorn.run("node:app", host="127.0.0.1", port=PORT, log_level="info")

if __name__ == "__main__":
    main()
