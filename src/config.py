import argparse

from ecdsa.curves import SECP256k1


class Config:
    ENV_TYPE = "DEVELOPMENT "  # "PRODUCTION"

    EXPOSE_API = False
    API_PORT = 6001
    API_HOST = "0.0.0.0"

    IPFS_PORT = 5001
    IPFS_HOST = "127.0.0.1"
    if ENV_TYPE == "PRODUCTION":
        IPFS_HOST = "ipfs-node"

    IS_TEST_NET = True
    IS_FULL_NODE = True
    ECDSA_CURVE = SECP256k1

    SCHEDULER_STEP_LENGTH = 1.0  # in seconds


def override_config():
    parser = argparse.ArgumentParser(description="Yoyocoin node daemon")
    parser.add_argument(
        "--expose-api", action="store_true", help="Expose http api for this node"
    )
    parser.add_argument(
        "--api-port", type=int, help="Port for the node external api (http)"
    )
    parser.add_argument(
        "--api-host", type=str, help="Host for the node external api (http)"
    )
    parser.add_argument("--ipfs-port", type=int, help="IPFS daemon port")
    parser.add_argument(
        "--test-net",
        "-t",
        default=Config.IS_TEST_NET,
        action="store_true",
        help="Run node with test net configuration",
    )
    parser.add_argument(
        "--prune-node", "-p", action="store_true", help="Only save blockchain summery"
    )
    args = vars(parser.parse_args())

    if args["api_port"] is not None:
        Config.API_PORT = args["api_port"]
    if args["api_host"] is not None:
        Config.API_HOST = args["api_host"]
    if args["ipfs_port"] is not None:
        Config.IPFS_PORT = args["ipfs_port"]
    Config.IS_TEST_NET = args.get("test_net", Config.IS_TEST_NET)
    Config.IS_FULL_NODE = not args.get("prune_node")
    Config.EXPOSE_API = args["expose_api"]
