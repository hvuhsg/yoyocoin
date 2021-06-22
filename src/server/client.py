import requests

REQUEST_TIMEOUT = 10
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
        return response.status_code == 200

    @staticmethod
    def get_block(url, block_hash):
        response = requests.get(url + "/get_block", params={"hash": block_hash}, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()["block"]

    @staticmethod
    def get_transaction(url, transaction_hash):
        response = requests.get(url + "/get_block", params={"hash": transaction_hash}, timeout=REQUEST_TIMEOUT)
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
            return
