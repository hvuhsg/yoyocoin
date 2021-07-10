from config import PORT
from scheduler import Scheduler

from ..nodes_list import NodesList, get_nodes_list
from ..connections_manager import ConnectionManager, get_connection_manager
from ..client import create_connection
from ..protocols.nodes_list_protocols import NodesListProtocol

__all__ = ["OutboundConnectionsMonitor"]


class OutboundConnectionsMonitor:
    def __init__(self):
        self.port = PORT

        # Scheduler.get_instance().add_job(
        #     func=self.check_connections_status,
        #     name="check_connections_status",
        #     interval=60*2,
        #     sync=False,
        #     run_thread=False,
        # )

        Scheduler.get_instance().add_job(
            func=self.fill_connection_pool,
            name="fill_connection_pool",
            interval=30,
            sync=False,
            run_thread=True,
        )
        Scheduler.get_instance().add_job(
            func=self.publish_my_address,
            name="publish_my_node_address",
            interval=60,
            sync=False,
            run_thread=True,
        )

    def fill_connection_pool(self):
        connection_manager: ConnectionManager = get_connection_manager()
        node_list: NodesList = get_nodes_list()
        for _ in range(connection_manager.max_outbound_connections - len(connection_manager.outbound_connections)):
            if connection_manager.outbound_connections_is_full():
                break
            address = node_list.get_random_node()
            if address in connection_manager.outbound_connections:
                continue
            create_connection(address)

    def publish_my_address(self):
        connection_manager: ConnectionManager = get_connection_manager()
        message = NodesListProtocol.publish(("127.0.0.1", PORT))
        connection_manager.broadcast(message)
