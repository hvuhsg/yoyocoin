from fastapi import FastAPI, Request, Depends, Response, status, BackgroundTasks
from json import loads

from blockchain import Blockchain, Block
from wallet import Wallet
from scheduler import Scheduler
from config import PORT

from .network_manager import NetworkManager
from .connections_monitor import ConnectionsMonitor
from .lottery_manager import LotteryManager
from .chain_syncer import ChainSyncer

app = FastAPI()

secret = input("Enter wallet secret: ")
if not secret:
    secret = None
wallet = Wallet(secret_passcode=secret)

blockchain = Blockchain(pruned=False, is_test_net=True)
lottery_manager: LotteryManager = None
syncer: ChainSyncer = None


def get_network_manager() -> NetworkManager:
    return NetworkManager.get_instance()


def get_connection_address(request: Request) -> tuple:
    return request.client.host, request.client.port


@app.on_event("startup")
async def startup():
    global lottery_manager
    global syncer
    scheduler = Scheduler(min_time_step=1)
    scheduler.daemon = True
    scheduler.start()

    nm = NetworkManager(max_outbound_connection=20, max_node_list=100, port=PORT)
    nm.setup()
    # Setup singleton

    ConnectionsMonitor(port=PORT)
    lottery_manager = LotteryManager(blockchain=blockchain, wallet=wallet)

    syncer = ChainSyncer(blockchain=blockchain, network_manager=nm, is_test_net=True)


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
    return {"score": blockchain.state.score, "length": blockchain.state.length, "hashs": blockchain.state.block_hashs}


@app.get("/blockchain_blocks")
def request_blockchain_blocks(start: int):
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
def get_lottery_block(block):
    block = loads(block)
    block = Block.from_dict(**block)
    lottery_manager.check_lottery_block(block)
    if block.index+1 > blockchain.chain_length:
        print(blockchain.chain_length, block.index)
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
        background_tasks.add_task(lambda: nm.broadcast_address(address))


@app.post("/ping")
def ping():
    return {"message": "pong"}
