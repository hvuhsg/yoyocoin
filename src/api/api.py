from fastapi import FastAPI, Depends

from blockchain import Blockchain, Transaction

from network import messages, Node

app = FastAPI(title="Node API")


def get_blockchain() -> Blockchain:
    blockchain: Blockchain = Blockchain.get_main_chain()
    return blockchain


@app.get("/wallets")
def wallets(limit: int = 10, offset: int = 0, blockchain: Blockchain = Depends(get_blockchain)):
    wallets_count = len(blockchain.state.sorted_wallets)
    return [
        w.to_dict()
        for w in blockchain.state.sorted_wallets[min(offset, wallets_count): min(offset+limit, wallets_count)]
    ]


@app.get("/wallet")
def wallet(address: str, blockchain: Blockchain = Depends(get_blockchain)):
    return blockchain.state.wallets.get(address, "wallet dose not exists")


@app.get("/block")
def block(index: int, blockchain: Blockchain = Depends(get_blockchain)):
    if index >= len(blockchain.chain):
        return "Block is not found (not full node or block is not forged yet)"
    return blockchain.chain[index].to_dict()


@app.get("/blocks")
def block(limit: int = 10, offset: int = 0, blockchain: Blockchain = Depends(get_blockchain)):
    chain_length = len(blockchain.chain)
    offset = min(chain_length, offset)
    limit = min(chain_length, limit)
    return [b.to_dict() for b in blockchain.chain[offset:min(limit+offset, chain_length)]]


@app.post("/transaction")
def broadcast_transaction(
        sender: str,
        recipient: str,
        amount: float,
        fee: float,
        signature: str,
        nonce: int,
        blockchain: Blockchain = Depends(get_blockchain),
):
    transaction = Transaction(
        sender=sender, recipient=recipient, amount=amount, fee=fee, signature=signature, nonce=nonce
    )
    blockchain.validate_transaction(transaction)

    messages.NewTransaction(
        transaction=transaction.to_dict(),
        hash=transaction.hash(),
        nonce=transaction.nonce
    ).send(node=Node.get_instance())
    print(sender, recipient, amount, fee, signature, nonce)
    return {"transaction": transaction.to_dict(), "broadcast": True}
