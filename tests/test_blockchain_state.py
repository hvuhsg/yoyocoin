from unittest import TestCase

from src.blockchain_state import BlockchainState


class BlockchainStateTestCase(TestCase):
    def setUp(self) -> None:
        self.state = BlockchainState()