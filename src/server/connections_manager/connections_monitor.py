from threading import Thread

from config import PORT
from scheduler import Scheduler
from client import Client

from .network_manager import NetworkManager


class ConnectionsMonitor:
    def __init__(self):
        self.port = PORT

        Scheduler.get_instance().add_job(
            func=self.check_connections_status,
            name="check_connections_status",
            interval=60*2,
            sync=False,
            run_thread=False,
        )
        Scheduler.get_instance().add_job(
            func=self.fill_connection_pool,
            name="fill_connection_pool",
            interval=10,
            sync=False,
            run_thread=True,
        )
        Scheduler.get_instance().add_job(
            func=self.publish_my_address,
            name="publish_my_node_address",
            interval=30,
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
        for node in nm.outbound_connections.copy():
            url = nm.url_from_address(node)
            Client.send_address(url, "0.0.0.0", self.port)
