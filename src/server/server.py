from fastapi import FastAPI, Request, Depends, BackgroundTasks
from json import loads

from blockchain import Blockchain, Block
from wallet import Wallet
from scheduler import Scheduler
from config import PORT

from consensus import LotteryManager, ChainSyncer
from .connections_manager import ConnectionsMonitor, NetworkManager

app = FastAPI()


def get_network_manager() -> NetworkManager:
    return NetworkManager.get_instance()


def get_connection_address(request: Request) -> tuple:
    return request.client.host, request.client.port


@app.on_event("startup")
async def startup():
    # Setup singleton's
    nm = NetworkManager(max_outbound_connection=20, max_node_list=100)
    nm.setup()

    ConnectionsMonitor()
    LotteryManager()
    ChainSyncer()


@app.on_event("shutdown")
async def shutdown():
    s: Scheduler = Scheduler.get_instance()
    s.stop()
    s.join()


@app.get("/block")
def request_block(block_hash: str):
    pass


@app.get("/transaction")
def request_transaction(transaction_hash: str):
    pass


@app.get("/blockchain_info")
def request_blockchain_info():
    blockchain = Blockchain.get_main_chain()
    return {"score": blockchain.state.score, "length": blockchain.state.length, "hashs": blockchain.state.block_hashs}


@app.get("/blockchain_blocks")
def request_blockchain_blocks(start: int):
    blockchain = Blockchain.get_main_chain()
    blocks = []
    for b in blockchain.chain[start:]:
        blocks.append(b.to_dict())
    return {"blocks": blocks}


@app.post("/nodes_list")
def request_nodes_list(max: int, network_manager: NetworkManager = Depends(get_network_manager)):
    return {"nodes": list(network_manager.nodes_list)[:min(len(network_manager.nodes_list), max)]}


@app.post("/connect")
def connect_to_node():
    return {"connected": True}


@app.get("/lottery_block")
def get_lottery_block(block: str):
    lottery_manager = LotteryManager.get_instance()
    blockchain = Blockchain.get_main_chain()
    syncer = ChainSyncer.get_instance()

    block = loads(block)
    block = Block.from_dict(**block)
    is_best = lottery_manager.check_lottery_block(block)
    if not is_best and block.index > blockchain.chain_length\
            or (block.index == blockchain.chain_length and block.previous_hash != blockchain.state.last_block_hash):
        syncer.sync()


@app.get('/address')
def get_node_address(
        host: str,
        port: int,
        background_tasks: BackgroundTasks,
        nm: NetworkManager = Depends(get_network_manager),
        address=Depends(get_connection_address),
):
    if host == "0.0.0.0":
        host = address[0]
    #  TODO: validate input
    address = (host, port)
    if port == PORT:  # Not allow self publish
        return  # TODO: change to ip check in prod

    if address not in nm.nodes_list:
        nm.add_to_node_list(address)
        # TODO: broadcast forward the address
        # background_tasks.add_task(lambda: nm.broadcast_address(address))


@app.post("/ping")
def ping():
    return {"message": "pong"}
