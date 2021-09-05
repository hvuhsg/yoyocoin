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
