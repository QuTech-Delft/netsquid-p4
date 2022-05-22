from netsquid.nodes import Node
from netsquid.protocols import NodeProtocol
from netsquid_netconf.builder import ComponentBuilder
from netsquid_netconf.netconf import netconf_generator
from pyp4.packet import Header, HeaderStack
import netsquid as ns

from examples.connections import ClassicalConnection
from netsquid_p4.components.v1model import V1ModelNode


class HostProtocol(NodeProtocol):

    def run(self):
        while True:
            yield self.await_port_input(self.node.port)
            packet = self.node.port.rx_input().items[0]
            print(f"[{ns.sim_time():>7}] Host {self.node.name} received: {packet}")
            self.node.port.tx_output(packet)


class HostNode(Node):

    def __init__(self, name, **properties):
        super().__init__(name, **properties)

        assert len(self.ports) == 1
        self.port = next(iter(self.ports.values()))

        self.__protocol = HostProtocol(self)
        self.__protocol.start()


def main():
    ComponentBuilder.add_type("classical_connection", ClassicalConnection)
    ComponentBuilder.add_type("v1model", V1ModelNode)
    ComponentBuilder.add_type("host", HostNode)
    generator = netconf_generator("./examples/ping_pong/netconf.yml")
    objects, _ = next(generator)

    host = objects["components"]["host"]

    switch = objects["components"]["switch"]
    switch.p4device.load("./examples/ping_pong/p4/ping-pong.json")

    hdr = Header([
        ("ttl", 8, False),
        ("ping_count", 32, False),
        ("last_time", 48, False),
        ("cur_time", 48, False),
    ])
    hdr["ttl"].val = 10

    ping = HeaderStack()
    ping.push(hdr)
    host.port.tx_output(ping)

    ns.sim_run(duration=200_000)


if __name__ == "__main__":
    main()
