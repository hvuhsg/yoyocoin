from fastapi import FastAPI, Depends

from blockchain import Blockchain


app = FastAPI(title="Node API")


def get_blockchain() -> Blockchain:
    blockchain: Blockchain = Blockchain.get_main_chain()
    return blockchain


@app.get("/wallets")
def wallets(limit: int = 10, offset: int = 0, blockchain=Depends(get_blockchain)):
    wallets_count = len(blockchain.state.sorted_wallets)
    return [
        w.to_dict()
        for w in blockchain.state.sorted_wallets[min(offset, wallets_count): min(offset+limit, wallets_count)]
    ]


@app.get("/wallet")
def wallet_balance(address: str, blockchain: Blockchain=Depends(get_blockchain)):
    return blockchain.state.wallets.get(address, "wallet dose not exists")
