from config import Config


class RemoteWallet:
    def __init__(
        self,
        public_address: str,
        balance: float,
        last_transaction: int,
        nonce_counter: int,
    ):
        self.address = public_address
        self.balance = balance
        self.last_transaction = last_transaction
        self.nonce_counter = nonce_counter

    @property
    def power(self) -> float:
        return self.balance / (self.last_transaction + 1)

    def to_dict(self):
        return {
            "address": self.address,
            "balance": self.balance,
            "last_transaction": self.last_transaction,
            "nonce": self.nonce_counter,
        }

    @classmethod
    def new_empty(cls, wallet_address: str):
        return cls(
            public_address=wallet_address,
            balance=1 if Config.IS_TEST_NET else 0,
            last_transaction=0,
            nonce_counter=0,
        )

    def __gt__(self, other) -> bool:
        return self.address > other.address

    def __eq__(self, other):
        return self.address == other.address

    def __repr__(self):
        return f"RW(address={self.address}, balance={self.balance})"
