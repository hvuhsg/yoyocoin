from fastapi import FastAPI, Request, Depends, Response, status
from json import loads

from blockchain import Blockchain, Block
from wallet import Wallet
from scheduler import Scheduler
from config import PORT

from .network_manager import NetworkManager
from .connections_monitor import ConnectionsMonitor
from .lottery_manager import LotteryManager

app = FastAPI()

secret = input("Enter wallet secret: ")
if not secret:
    secret = None
wallet = Wallet(secret_passcode=secret)

blockchain = Blockchain(is_test_net=True)
lottery_manager: LotteryManager = None


def get_network_manager() -> NetworkManager:
    return NetworkManager.get_instance()


def get_connection_address(request: Request) -> tuple:
    return request.client.host, request.client.port


@app.middleware("http")
async def inbound_only_middleware(
        request: Request,
        call_next,
):
    network_manager = get_network_manager()
    ip = get_connection_address(request)[0]
    if ip in network_manager.inbound_connections or request.method.upper() != "GET":
        response = await call_next(request)
    else:
        response = Response("not inbound connection", status.HTTP_403_FORBIDDEN)
    return response


@app.on_event("startup")
async def startup():
    global lottery_manager
    scheduler = Scheduler(min_time_step=1)
    scheduler.daemon = True
    scheduler.start()

    nm = NetworkManager(max_inbound_connection=20, max_outbound_connection=20, max_node_list=100, port=PORT)
    nm.setup()
    # Setup singleton

    ConnectionsMonitor(port=PORT)
    lottery_manager = LotteryManager(blockchain=blockchain, wallet=wallet)


@app.on_event("shutdown")
async def shutdown():
    s: Scheduler = Scheduler.get_instance()
    s.stop()
    s.join()


@app.get("/block")
async def request_block(block_hash: str):
    pass


@app.get("/transaction")
async def request_transaction(transaction_hash: str):
    pass


@app.get("/blockchain_info")
async def request_blockchain_info():
    return {"score": blockchain.state.score, "length": blockchain.state.length, "hashs": blockchain.state.block_hashs}


@app.get("/blockchain_blocks")
async def request_blockchain_blocks(start: int, end: int = -1):
    blocks = []
    for b in blockchain.chain[start:end]:
        blocks.append(b.to_dict())
    return {"blocks": blocks}


@app.post("/nodes_list")
async def request_nodes_list(max: int, network_manager: NetworkManager = Depends(get_network_manager)):
    return {"nodes": list(network_manager.nodes_list)[:min(len(network_manager.nodes_list), max)]}


@app.post("/connect")
async def connect_to_node(request: Request, network_manager: NetworkManager = Depends(get_network_manager)):
    ip = request.client.host
    if True:  # network_manager.can_add_inbound_connection(ip):
        network_manager.add_inbound_connection(ip)
        return {"connected": True}
    return {"connected": False}


@app.get("/lottery_block")
async def get_lottery_block(block):
    block = loads(block)
    block = Block.from_dict(**block)
    lottery_manager.check_lottery_block(block)


@app.get('/address')
async def get_node_address(
        host: str,
        port: int,
        nm: NetworkManager = Depends(get_network_manager),
        address=Depends(get_connection_address),
):
    if host == "0.0.0.0":
        host = address[0]
    #  TODO: validate input
    address = (host, port)
    nm.add_to_node_list(address)
    nm.broadcast_address(address)


@app.post("/ping")
async def ping():
    return {"message": "pong"}
