BLOCKS_PER_MINUTE = 1

BLOCK_COUNT_FREEZE_WALLET_LOTTERY_AFTER_WIN = (
    BLOCKS_PER_MINUTE * 60 * 24 * 7
)  # one week

NETWORK_START_TIME = (
    0  # TODO: set to network start time (unix time) for timestamp validation
)
# So blocks cant be created before time


DEVELOPER_KEY = "029afdebc63d5f25a275ae21d301fbc7449e0769320a3cfd4160700c35c5768c72"

GENESIS_BLOCK = {
    "index": 0,
    "timestamp": 1631197494.0218372,
    "transactions": [
        {
            "sender": "0",
            "recipient": "029afdebc63d5f25a275ae21d301fbc7449e0769320a3cfd4160700c35c5768c72",
            "amount": 1000000000000,
            "fee": 0,
            "nonce": 0,
            "signature": "MTEwMTgxMjIxMjI0MTAxMjQ0ODEyNzI3OTA2ODUxOTQ5MDQ1MjczOTQ5NjQ0MDEzOTc3MDA4NzAxOTM0NTE0NzA2NDczNjI2MzIxNjE0OjM4MDc3MzYwMTc2NjIzMjc4NTg4MDY5NDE5Mzg4NTkyNjE5MzkzMzQwNzQyMTY4MTYzNjY4MzYwNzI2NjM1MzM2ODEwMjQ5ODAzNTU=",
        }
    ],
    "previous_hash": "0",
    "forger": "029afdebc63d5f25a275ae21d301fbc7449e0769320a3cfd4160700c35c5768c72",
    "hash": "c5163f64e379de56a585007c78f50034f10e175f3587be896ea67d22825309a3",
    "signature": "NzMxNDYyMjQwMzIwNTg5MzAxNDg1NTEwNTMyMjI4NjkzMTk5MTA2NTM4NjEzNDY2MzYyNDYxNzkzODE4MzI4NzY2ODg5NTQ0MDIxNzozMzE4NzE4MDE3MDcxODY3Mjc3NzI5MjA1NTE2NTU1NjIyNjAzMDI0NDI0MjExNjkxOTY5OTc1MDUwOTI0NzE0NzI4MjkzNDQ1NDcxMw==",
}
