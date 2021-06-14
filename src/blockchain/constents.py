BLOCKS_PER_MINUTE = 1

BLOCK_COUNT_FREEZE_WALLET_LOTTERY_AFTER_WIN = (
    BLOCKS_PER_MINUTE * 60 * 24 * 7
)  # one week

NETWORK_START_TIME = (
    0  # TODO: set to network start time (unix time) for timestamp validation
)
# So blocks cant be created before time


DEVELOPER_KEY = "cra+B7ntFLH7Xxyt5ow96BB53znXPId0SNLMw4GNKl/Gs0qvmo4BLYfmS8ukQl1m"

GENESIS_BLOCK = {
    "index": 0,
    "timestamp": 1622137530.5758097,
    "transactions": [
        {
            "sender": "cra+B7ntFLH7Xxyt5ow96BB53znXPId0SNLMw4GNKl/Gs0qvmo4BLYfmS8ukQl1m",
            "recipient": "cra+B7ntFLH7Xxyt5ow96BB53znXPId0SNLMw4GNKl/Gs0qvmo4BLYfmS8ukQl1m",
            "amount": 1000,
            "fee": 1,
            "nonce": 0,
            "hash": "1973f4016652e14c7d4ceb80992553d0d7861c882ba24ca414e0c4e18b756a94",
            "signature": "6U8JdOSEKdamWQn/NFvE9T3VcJtL2GqeD/ZhyuXItfZaAjcu37ae0FtTwBjHf2XF",
        }
    ],
    "previous_hash": "0",
    "forger": "cra+B7ntFLH7Xxyt5ow96BB53znXPId0SNLMw4GNKl/Gs0qvmo4BLYfmS8ukQl1m",
    "hash": "c82993ce06e6fc7430f3e2a72acbbed42afb5141c4dac2ca9e1e8e1ef95493d2",
    "signature": "icZgIY8RP1HzSF39UQFn3be+o0KsJ3u0MPIwO+Q8E43grJVQhMMKTwlb0PTtwzCI",
}

MAX_BLOCKS_FOR_SCORE = 200
MAX_BALANCE_FOR_SCORE = 100_000_000
BLOCKS_CURVE_NUMBER = 120
MIN_SCORE = 0.1

LOTTERY_PRIZES = [1, 2, 4, 8, 16]
LOTTERY_WEIGHTS = [0.823, 0.1, 0.05, 0.025, 0.001]
