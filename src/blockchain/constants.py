BLOCKS_PER_MINUTE = 1

BLOCK_COUNT_FREEZE_WALLET_LOTTERY_AFTER_WIN = (
    BLOCKS_PER_MINUTE * 60 * 24 * 7
)  # one week

NETWORK_START_TIME = (
    0  # TODO: set to network start time (unix time) for timestamp validation
)
# So blocks cant be created before time


DEVELOPER_KEY = "046fd97bd6ee9f45f8298fb9bb2706258a9f42ff0ca54d2e351888808ac239044dae0c28a7d3c664175bc41b594f9fb1f1bf7887f2488a882268ba36d4813c14"

GENESIS_BLOCK = {
    "index": 0,
    "timestamp": 1628516978.7534876,
    "transactions": [
        {
            "sender": "0",
            "recipient": "046fd97bd6ee9f45f8298fb9bb2706258a9f42ff0ca54d2e351888808ac239044dae0c28a7d3c664175bc41b594f9fb1f1bf7887f2488a882268ba36d4813c14",
            "amount": 1_000_000_000_000,
            "fee": 0,
            "nonce": 0,
            "hash": "c59d08b266b9d534364d760d3699a0a3aa10c6fd7c5119cf3dec7609d8d8e3ed",
            "signature": "bAjmceXFYqLOx6Orztg/y35C+8Zx9daw5P+DDNqiRIvFin9NFnrMYMAarBIy0VsIif8onhMJPgvkrE+iQ7NN3g==",
        }
    ],
    "previous_hash": "0",
    "forger": "046fd97bd6ee9f45f8298fb9bb2706258a9f42ff0ca54d2e351888808ac239044dae0c28a7d3c664175bc41b594f9fb1f1bf7887f2488a882268ba36d4813c14",
    "hash": "a32a287f685e80843a278c0f5c36c3beb7a80380a495b8cb3c1ae0d03fab4ec3",
    "signature": "poQ7WbOzCC7IKQI+IcYUGb6RZfV/faIGPCK+pVgy4frmlkdhggfBEAZ4w6OWGwJXLx6lXuz8puAZwkECoPdMIg==",
}
