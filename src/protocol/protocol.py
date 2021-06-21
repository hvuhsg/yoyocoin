from blockchain import Transaction, Block, Blockchain, ValidationError
from node import MessageFactory


class Protocol:
    def __init__(self, blockchain: Blockchain, is_test_net: bool, update_blockchain_callback, sync_node):
        self.sync_node = sync_node
        self.blockchain = blockchain
        self.best_block = None
        self.best_score = 0
        self.message_factory = MessageFactory.get_instance()
        self.is_test_net = is_test_net
        self.sync_chain_info = None
        self.sync_chain_change_index = 0
        self.is_sync = False
        self.update_blockchain_callback = update_blockchain_callback

    def insert_new_blocks(self):
        if self.best_block is None:
            return
        try:
            self.blockchain.add_block(self.best_block)
        except ValidationError as VE:
            print("insert", VE, type(VE))
        else:
            print("insert block", self.best_block.index, self.best_block.hash())
        finally:
            self.best_score = 0
            self.best_block = None

    def check_block_score(self, block):
        try:
            block.validate(blockchain_state=self.blockchain.state, is_test_net=True)
        except ValidationError as VE:
            print(VE)
            self.sync_node()
            return
        block_score = self.blockchain.state.block_score(block)
        if block_score > self.best_score:
            print("new best block", block.hash(), block.index)
            self.best_score = block_score
            self.best_block = block

    def new_block(self, message):
        block = message.payload
        block = Block.from_dict(**block)
        self.check_block_score(block)

    def new_transaction(self, message):
        transaction = message.payload
        transaction = Transaction.from_dict(**transaction)
        transaction.validate(blockchain_state=self.blockchain.state, is_test_net=True)
        self.blockchain.current_transactions.append(transaction)

    def chain_info(self, message):
        score = self.blockchain.state.score
        length = self.blockchain.state.length
        hashs = self.blockchain.state.block_hashs
        data = {"score": score, "length": length, "hashs": hashs}
        response_message = self.message_factory.route_response(data, route=message.route)
        return response_message

    def chain_info_response(self, message):
        info = message.payload
        if info["score"] < self.blockchain.state.score or info["length"] < self.blockchain.state.length:
            return
        if len(info["hashs"]) != info["length"]:
            return
        self.sync_chain_info = info
        start = 0
        for my, he in zip(self.blockchain.state.block_hashs, info["hashs"][:self.blockchain.state.length]):
            print(my, he)
            if my == he:
                start += 1
        self.sync_chain_change_index = start
        message = self.message_factory.get_chain_history({"start": start, "end": info["length"]})
        return message

    def chain_blocks_response(self, message):
        sync_chain = Blockchain(is_test_net=self.is_test_net)
        if self.sync_chain_change_index > 0 and not self.blockchain.pruned:
            for b in self.blockchain.chain[1:self.sync_chain_change_index]:
                sync_chain.add_block(b)

        blocks_data = message.payload
        for index, b in enumerate(blocks_data):
            block = Block.from_dict(**b)
            if block.hash() != self.sync_chain_info["hashs"][index+1]:
                return
            sync_chain.add_block(block)
        print("synced", sync_chain.state.score, sync_chain.state.length, self.blockchain.state.score, self.blockchain.state.length)
        if sync_chain.state.score > self.blockchain.state.score and sync_chain.state.length >= self.blockchain.state.length:
            print(sync_chain.state.length, sync_chain.state.score)
            self.blockchain = sync_chain
            self.is_sync = True
            self.update_blockchain_callback(self.blockchain)
        else:
            self.sync_chain_info = None
            self.sync_chain_change_index = 0

    def chain_blocks(self, message):
        slice_info = message.payload
        if self.blockchain.pruned:
            return
        blocks = [b.to_dict() for b in self.blockchain.chain[slice_info["start"]: slice_info["end"]]]
        message = self.message_factory.route_response(blocks, route=message.route)
        return message
