from bisect import bisect_left

from .sum_tree import SumTree
from ..remote_wallet import RemoteWallet


def binary_search(array, element):
    i = bisect_left(array, element)
    if i != len(array) and array[i] == element:
        return i
    else:
        return -1


def find_lottery_winner(root: SumTree, lottery_number: float) -> int:
    """
    Find lottery winner index

    :param root: the root node of the sum tree
    :param lottery_number: float number in range of 0 to 1
    :return: winner wallet index
    """
    search_number = lottery_number * root.sum
    winner = root.search(search_number)
    return winner


def wallet_distance(winner_index: int, wallet_index: int, wallets_count: int):
    # The 0.1 is added for tie break
    # TODO: replace 100 - X with more robust option
    return 100 - min(
        abs(winner_index - wallet_index) + 0.1,
        winner_index + (wallets_count - wallet_index),
    )


def wallet_score(
    root: SumTree,
    wallet: RemoteWallet,
    lottery_number: float,
    wallets_sorted_by_address: list,
):
    wallets_count = len(wallets_sorted_by_address)
    winner_index = find_lottery_winner(root, lottery_number)
    wallet_index = binary_search(wallets_sorted_by_address, wallet)
    return wallet_distance(winner_index, wallet_index, wallets_count)
