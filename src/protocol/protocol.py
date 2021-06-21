from blockchain import Transaction, Block, Blockchain
from node import MessageFactory


class Protocol:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.best_blocks = {}
        self.message_factory = MessageFactory.get_instance()

    def insert_new_blocks(self):
        if self.best_blocks:
            blocks = map(lambda kv: kv[1][0], sorted(self.best_blocks.items(), key=lambda kv: kv[0]))
            for b in blocks:
                print("insert", b.hash(), b.index)
                self.blockchain.add_block(b)
        self.best_blocks = {}

    def check_block_score(self, block):
        block.validate(blockchain_state=self.blockchain.state, is_test_net=True)
        block_score = self.blockchain.state.block_score(block)
        best_block, best_score = self.best_blocks.get(block.index, (None, 0))
        if block_score > best_score:
            print("new best block", block.hash())
            self.best_blocks[block.index] = (block, block_score)

    def new_block(self, block):
        block = Block.from_dict(**block)
        self.check_block_score(block)

    def new_transaction(self, transaction):
        transaction = Transaction.from_dict(**transaction)
        transaction.validate(blockchain_state=self.blockchain.state, is_test_net=True)
        self.blockchain.current_transactions.append(transaction)

    def chain_info(self, message, node):
        score = self.blockchain.state.score
        length = self.blockchain.state.length
        hashs = self.blockchain.state.block_hashs
        data = {"score": score, "length": length, "hashs": hashs}
        response_message = self.message_factory.route_response(data, route=message.route)
        return response_message

    def chain_blocks(self, slice_info):
        if self.blockchain.pruned:
            return
