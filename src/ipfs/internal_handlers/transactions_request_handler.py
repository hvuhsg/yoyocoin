from ..api import Message, IpfsAPI, MessageType


class TransactionsRequestHandler:
    def __init__(self, ipfs_api: IpfsAPI, my_node_id: str):
        self.ipfs_api = ipfs_api
        self.my_node_id = my_node_id

        self.transactions_info_cid = None

    def _get_transactions_info_cid(self) -> str:
        # TODO: if transactions info cid is none upload chain info to ipfs and get cid
        pass

    def _transactions_info_message(self) -> Message:
        return Message(
            type=MessageType.TRANSACTIONS_INFO,
            cid=self._get_transactions_info_cid(),
        )

    def handle_request(self, message: Message, topic: str):
        if not message.meta:
            return
        node_id = message.meta.get("node_id", None)
        if node_id is None or node_id == self.my_node_id:
            return

        response_topic = topic+"-"+node_id
        self.ipfs_api.publish_json_to_topic(topic=response_topic, data=self._transactions_info_message().to_dict())
