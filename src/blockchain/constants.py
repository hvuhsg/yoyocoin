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
    'index': 0,
    'timestamp': 1627912767.7128441,
    'transactions': [
        {
            'sender': '046fd97bd6ee9f45f8298fb9bb2706258a9f42ff0ca54d2e351888808ac239044dae0c28a7d3c664175bc41b594f9fb1f1bf7887f2488a882268ba36d4813c14',
            'recipient': '046fd97bd6ee9f45f8298fb9bb2706258a9f42ff0ca54d2e351888808ac239044dae0c28a7d3c664175bc41b594f9fb1f1bf7887f2488a882268ba36d4813c14',
            'amount': 1000000000000,
            'fee': 0,
            'nonce': 0,
            'hash': '2707796f45871e96ea034c6a0eb5df3ab60f4a1063625ad5f5ba354b64abced5',
            'signature': '9QMx6Ea8cohx0Asz35qB6g4VUFqAdw7pzuw2ttGEUhbcBARSMcgYa7aGlC5e4siXNjW5dgdinzzTCYBg+4ANFg=='
        }
    ],
    'previous_hash': '0',
    'forger': '046fd97bd6ee9f45f8298fb9bb2706258a9f42ff0ca54d2e351888808ac239044dae0c28a7d3c664175bc41b594f9fb1f1bf7887f2488a882268ba36d4813c14',
    'hash': 'd809ea411cd2c9de31b61fe62b49605d35bd773a8fbd60a796d3940e999bdad9',
    'signature': 'Qg4fY5XWYSJWPNjNIVLKJwAjIT5sT0YY+/JjjRVoJq88S25vjL5NatwJFSVGebbrl0cjUxOs02CYH2SVNyIvtg=='
}
