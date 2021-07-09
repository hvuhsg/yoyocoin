import requests
from json import dumps

REQUEST_TIMEOUT = 10
SHORT_TIMEOUT = 4
PING_TIMEOUT = 60


class Client:
    @staticmethod
    def ping(url) -> bool:
        """
        Check connection with node

        :param url: url of node
        :return: True if response to ping with code 200 else False
        """
        try:
            response = requests.post(url + "/ping", timeout=PING_TIMEOUT)
        except requests.ConnectionError:
            return False
        except requests.ReadTimeout:
            return False
        return response.status_code == 200

    @staticmethod
    def get_transaction(url, transaction_hash):
        response = requests.get(url + "/transaction", params={"hash": transaction_hash}, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()["transaction"]

    @staticmethod
    def get_nodes_list(url, max_count=100):
        try:
            response = requests.post(url + "/nodes_list", params={"max": max_count}, timeout=REQUEST_TIMEOUT)
        except requests.ConnectionError:
            return []
        if response.status_code == 200:
            return response.json()["nodes"]

    @staticmethod
    def connect_to_node(url):
        try:
            response = requests.post(url + "/connect", timeout=REQUEST_TIMEOUT)
        except requests.ConnectionError:
            return False
        if response.status_code == 200 and response.json().get("connected", False):
            return True
        return False

    @staticmethod
    def send_address(url, host, port):
        try:
            requests.get(url + "/address", params={"host": host, "port": port}, timeout=REQUEST_TIMEOUT)
        except requests.ConnectionError:
            pass
        except requests.ReadTimeout:
            pass

    @staticmethod
    def send_best_lottery_block(url, block_dict: dict) -> bool:
        try:
            return requests.get(
                url + "/lottery_block", params={"block": dumps(block_dict)}, timeout=REQUEST_TIMEOUT
            ).json()["ok"]
        except requests.ConnectionError:
            pass
        except requests.ReadTimeout:
            pass

    @staticmethod
    def get_chain_blocks(url, start: int):
        try:
            return requests.get(url + "/blockchain_blocks", params={"start": start}, timeout=REQUEST_TIMEOUT).json()
        except requests.ConnectionError:
            pass
        except requests.ReadTimeout:
            pass

    @staticmethod
    def request_chain_info(url):
        try:
            return requests.get(url + "/blockchain_info", timeout=SHORT_TIMEOUT).json()
        except requests.ConnectionError:
            pass
        except requests.ReadTimeout:
            pass

    @staticmethod
    def gossip_transaction(url: str, transaction_hash: str):
        try:
            return requests.post(url + "/transaction_hash", timeout=SHORT_TIMEOUT).json()
        except requests.ConnectionError:
            pass
        except requests.ReadTimeout:
            pass
