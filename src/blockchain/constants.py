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
    'index': 0,
    'timestamp': 1631130650.4518838,
    'transactions': [
        {
            'sender': '0',
            'recipient': '029afdebc63d5f25a275ae21d301fbc7449e0769320a3cfd4160700c35c5768c72',
            'amount': 1000000000000,
            'fee': 0,
            'nonce': 0,
            'hash': '52a0d0174dd50b0153f8552467d2b0963b187d5ee3c72ceede8adbdfcee1d641',
            'signature': 'NzA1NzUwMDUyNzU4MzkyNjczNDkzNDMzOTk5OTUyOTAyNTkxMTY3Njc3NjAzNzk1NDAxNDA5MzM0NjM0MTcwNDg2NzAyMDg3NTcxNzoxMDI2MDM4MDIxNjczODcxMzEwNjY3NjQ3Mzg2MTMyODI3MjE0OTg3NzQ3Mjk3MjQ2OTAwODM3OTM1MTE2NjE3NTg1MTg3MjY3OTc5NzM=',
        }
    ],
    'previous_hash': '0',
    'forger': '029afdebc63d5f25a275ae21d301fbc7449e0769320a3cfd4160700c35c5768c72',
    'hash': 'ddcc9589a0929ebf83d84a1a977206f48f2bffc56fe6914266a58ed9ace274e6',
    'signature': 'NDQ5NTM4MzA3OTE3OTkzMzU5MTA1MTg2NzMzNDEyODYyMjc0MzI0NTQxNjE3NjI2MDY0NDk5MDc5NTM4MTE2NjA3MTcxODY2NDg2MTg6MjIzMzcyNTM5OTYzOTAyNDIyNDU1MjgzNzc5NDMyNjM5ODE4ODQ2ODkxMDA5MjQzNzczNDk4NDgzNzY3MDM1NDMxNTkxNzM5ODQ2MTI=',
}
