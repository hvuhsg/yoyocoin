import requests
import json
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
from base64 import b64decode
from uuid import uuid4


__all__ = ["Message", "MessageType", "IpfsAPI", "message_serializer", "MessageInterface"]


class MessageType(Enum):
    GET_CHAIN = "get-chain"
    CHAIN_INFO = "chain-info"

    GET_TRANSACTIONS = "get-transactions"
    TRANSACTIONS_INFO = "transactions-info"

    NEW_TRANSACTION = "new-transaction"
    NEW_BLOCK = "new-block"

    TEST = "test"


class MessageInterface(ABC):
    @abstractmethod
    def has_node_id(self) -> bool:
        return NotImplemented

    @abstractmethod
    def get_node_id(self) -> str:
        return NotImplemented


@dataclass
class Message(MessageInterface):
    type: MessageType
    meta: dict = None
    cid: str = None

    def to_dict(self):
        return {
            "type": self.type.value,
            "meta": self.meta,
            "cid": self.cid,
        }

    def has_node_id(self) -> bool:
        return "node_id" in self.meta

    def get_node_id(self) -> str:
        return self.meta["node_id"]


def message_serializer(message: str) -> Message:
    try:
        message_dict = json.loads(message)
    except json.JSONDecodeError:
        cid = message
        message_type = MessageType.TEST
        meta = None
    else:
        message_type = MessageType(message_dict.pop("type"))
        cid = message_dict.pop("cid", None)
        meta = message_dict["meta"]
    return Message(type=message_type, cid=cid, meta=meta)


class IpfsAPI:
    def __init__(self, host="127.0.0.1", port=5001):
        self.host = host
        self.port = port

        self.node_id = str(uuid4())

        self.base_api_url = f"http://{self.host}:{self.port}/api/v0"

        self.node_info = self.get_node_info()

    def get_node_info(self) -> str:
        response = requests.post(self.base_api_url + "/version")
        return response.json()

    def get_pubsub_peers(self, topic: str = None) -> list:
        params = {}
        if topic:
            params = {"arg": topic}
        response = requests.post(self.base_api_url + "/pubsub/peers", params=params)
        return response.json()["Strings"]

    def get_sync_peers(self) -> str:
        return self.get_pubsub_peers("sync")

    def add_data(self, data: str):
        files = {'content': data}
        response = requests.post(self.base_api_url + "/block/put", files=files)
        return response.json()

    def get_data(self, cid: str):
        response = requests.post(self.base_api_url + "/block/get", params={"arg": cid})
        return response.text

    def block_stat(self, cid: str):
        response = requests.post(self.base_api_url + "/block/stat", params={"arg": cid})
        return response.json()

    def _publish_to_topic(self, topic: str, data: str):
        response = requests.post(self.base_api_url + "/pubsub/pub", params={"arg": [topic, data]})
        return response.text

    def publish_json_to_topic(self, topic: str, data: dict):
        json_data = json.dumps(data)
        response = self._publish_to_topic(topic, data=json_data)
        return response

    def sub_to_topic(self, topic: str):
        response = requests.post(self.base_api_url + "/pubsub/sub", params={"arg": topic}, stream=True)
        data = b""
        for stream_data in response:
            data += stream_data
            if stream_data.endswith(b"\n"):
                data = json.loads(data)
                data["data"] = b64decode(data["data"])
                yield data
                data = b""

if __name__ == "__main__":
    node = IpfsAPI()
    print(node.node_info)
    cid = node.add_data("hello mt")["Key"]
    print(cid)
    print(node.get_data(cid))
    print(node.block_stat(cid))
    print(node.publish_json_to_topic("test", {"hi": True}))
    for m in node.sub_to_topic("test"):
        print(m)
