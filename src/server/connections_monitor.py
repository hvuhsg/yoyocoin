from threading import Thread
from time import sleep

from .network_manager import NetworkManager
from .client import Client


class ConnectionsMonitor(Thread):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.daemon = True
        self._stop = False
        self.port = port

    @staticmethod
    def _check_connection_status(address):
        nm: NetworkManager = NetworkManager.get_instance()
        url = nm.url_from_address(address)
        if not Client.ping(url):
            nm.outbound_connections.remove(address)

    def run(self):
        nm: NetworkManager = NetworkManager.get_instance()
        counter = 0
        while not self._stop:
            for _ in range(60):
                sleep(1)
                if self._stop:
                    break
            if not nm.outbound_connections_is_full():
                nm.make_outbound_connections()
            for node in nm.outbound_connections:
                t = Thread(target=self._check_connection_status, args=[node])
                t.daemon = True
                t.start()
            if counter % 10 == 0 or counter == 0:
                nm.broadcast_address(("0.0.0.0", self.port))
            counter += 1

    def stop(self):
        self._stop = True
