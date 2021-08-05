from ecdsa.curves import SECP256k1

### Environment
ENV_TYPE = "DEVELOPMENT "  # "PRODUCTION"


### Network
API_PORT = 6001

IPFS_PORT = 5001
IPFS_HOST = "127.0.0.1"

if ENV_TYPE == "PRODUCTION":
    IPFS_HOST = "ipfs-node"

### Blockchain
IS_TEST_NET = True

IS_FULL_NODE = True

ECDSA_CURVE = SECP256k1

### Manager
SCHEDULER_STEP_LENGTH = 1.0  # in seconds
