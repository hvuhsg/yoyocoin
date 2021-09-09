from wallet import Wallet
from blockchain import Transaction, Block


def create_genesis(developer_secret: str):
    wallet = Wallet(secret_passcode=developer_secret)
    print("GENESIS_WALLET_ADDRESS:", wallet.public)

    g_transaction = Transaction(
        sender="0", recipient=wallet.public, amount=1000000000000, nonce=0, fee=0
    )
    signature = wallet.sign(g_transaction.hash())
    g_transaction.signature = signature

    g_block = Block(
        forger=wallet.public, index=0, previous_hash="0", transactions=[g_transaction]
    )
    signature = wallet.sign(g_block.hash())
    g_block.signature = signature
    print(g_block.to_dict())
    return g_block
