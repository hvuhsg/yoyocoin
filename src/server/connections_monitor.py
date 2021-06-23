from threading import Thread

from scheduler import Scheduler

from .network_manager import NetworkManager
from .client import Client


class ConnectionsMonitor:
    def __init__(self, port):
        self.port = port

        Scheduler.get_instance().add_job(
            func=self.check_connections_status,
            name="check_connections_status",
            interval=20,
            sync=False,
            run_thread=False,
        )
        Scheduler.get_instance().add_job(
            func=self.fill_connection_pool,
            name="fill_connection_pool",
            interval=5,
            sync=False,
            run_thread=True,
        )
        Scheduler.get_instance().add_job(
            func=self.publish_my_address,
            name="publish_my_node_address",
            interval=5,
            sync=False,
            run_thread=True,
        )

    @staticmethod
    def _check_connection_status(address):
        nm: NetworkManager = NetworkManager.get_instance()
        url = nm.url_from_address(address)
        if not Client.ping(url):
            nm.outbound_connections.remove(address)

    def check_connections_status(self):
        nm: NetworkManager = NetworkManager.get_instance()
        for node in nm.outbound_connections:
            t = Thread(target=self._check_connection_status, args=[node])
            t.daemon = True
            t.start()

    def fill_connection_pool(self):
        nm: NetworkManager = NetworkManager.get_instance()
        if not nm.outbound_connections_is_full():
            nm.make_outbound_connections()

    def publish_my_address(self):
        nm: NetworkManager = NetworkManager.get_instance()
        nm.broadcast_address(("0.0.0.0", self.port))
