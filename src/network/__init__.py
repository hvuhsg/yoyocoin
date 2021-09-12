from .ipfs import Node, setup_node

from .subscribers import setup_subscribers


def setup_network():
    setup_node()
    setup_subscribers()


__all__ = ["Node", "setup_network"]
