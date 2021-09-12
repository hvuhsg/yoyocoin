from time import sleep
import sys

from loguru import logger

import api
from config import Config, override_config
from event_stream import setup_event_stream, Event
from wallet import Wallet
from blockchain import setup_blockchain
from scheduler import setup_scheduler
from network import setup_network
from chain_extender import setup_global_loop_handler
from protocol import setup_protocol
from helpers import create_genesis


def setup_wallet():
    secret = "test-key"
    if not secret:
        secret = None
    wallet = Wallet(secret_passcode=secret)
    Wallet.set_main_wallet(wallet)


def setup_api():
    api.run()


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

    event_stream = setup_event_stream()
    setup_wallet()
    scheduler = setup_scheduler()
    setup_blockchain()
    setup_network()
    setup_global_loop_handler()
    setup_protocol()
    scheduler.start()

    event_stream.publish(topic="lifecycle", event=Event("end-setup"))
    if Config.EXPOSE_API:
        setup_api()
    idle()

    event_stream.publish(topic="lifecycle", event=Event("closing"))
    # Stopping
    scheduler.stop()
    # TODO: close storage


if __name__ == "__main__":
    main()
    # create_genesis("YOYO_DEVELOP_PASS")
