from fastapi import FastAPI

from blockchain import Blockchain


app = FastAPI(title="Node API")


@app.get("/wallets")
def wallets(limit: int = 10, offset: int = 0):
    blockchain: Blockchain = Blockchain.get_main_chain()
    wallets_count = len(blockchain.state.sorted_wallets)
    return [
        w.to_dict()
        for w in blockchain.state.sorted_wallets[min(offset, wallets_count): min(offset+limit, wallets_count)]
    ]


@app.get("/")
def wallet_balance(address: str):
    return 5
