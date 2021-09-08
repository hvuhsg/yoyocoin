from .ipfs import Message, Node


class SyncRequest:
    topic = "chain-request"

    def __init__(self, score: int, length: int):
        self.score = score
        self.length = length

    def to_message(self) -> Message:
        return Message(meta={"score": self.score, "length": self.length})

    def send(self, node: Node):
        node.publish_to_topic(topic=self.topic, message=self.to_message())


class NewBlock:
    topic = "new-block"

    def __init__(self, block: dict, privies_hash: str, index: int):
        self.block = block
        self.privies_hash = privies_hash
        self.index = index

    def to_message(self, cid: str) -> Message:
        return Message(meta={"p_hash": self.privies_hash, "index": self.index}, cid=cid)

    def send(self, node: Node):
        cid = node.create_cid(self.block)
        node.publish_to_topic(topic=self.topic, message=self.to_message(cid))


class NewTransaction:
    topic = "new-transaction"

    def __init__(self, transaction: dict, hash: str, nonce: int):
        self.transaction = transaction
        self.hash = hash
        self.nonce = nonce

    def to_message(self, cid: str) -> Message:
        return Message(meta={"hash": self.hash, "nonce": self.nonce}, cid=cid)

    def send(self, node: Node):
        cid = node.create_cid(self.transaction)
        node.publish_to_topic(topic=self.topic, message=self.to_message(cid))
