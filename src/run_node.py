from time import sleep
from .node import BlockchainNode


my_node = BlockchainNode()

my_node.start()
sleep(1)

# TODO: Connect to list of node's
# if you did not generate list of node's, use existing node to create list of node's

my_node.send_to_nodes("greetings")  # introduce you'r self to the network
