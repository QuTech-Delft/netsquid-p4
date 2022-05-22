from copy import deepcopy
from ipaddress import ip_address
import json

from netsquid.nodes import Node
from netsquid.protocols import NodeProtocol
from netsquid_netconf.builder import ComponentBuilder
from netsquid_netconf.netconf import netconf_generator
from pyp4.packet import HeaderStack
from pyp4.processors.v1model import V1ModelProcess

import netsquid as ns
import pyp4

from examples.connections import ClassicalConnection
from netsquid_p4.components.v1model import V1ModelNode


class mac_address:

    def __init__(self, mac):
        self.__mac = mac.split(':')

    def __int__(self):
        return int(''.join(self.__mac), 16)


class HostProtocol(NodeProtocol):

    def run(self):
        while True:
            yield self.await_port_input(self.node.port)
            packet = self.node.port.rx_input().items[0]

            eth = packet.pop()
            ipv4 = packet.pop()

            print(f"[{ns.sim_time():>6}] Host {self.node.name} received: "
                  f"{packet.payload}\" (TTL: {ipv4['ttl']})")

            if packet.payload.startswith("Ping"):
                eth["srcAddr"].val, eth["dstAddr"].val = eth["dstAddr"].val, eth["srcAddr"].val
                ipv4["srcAddr"].val, ipv4["dstAddr"].val = ipv4["dstAddr"].val, ipv4["srcAddr"].val

                packet.push(ipv4)
                packet.push(eth)
                packet.payload = packet.payload.replace("Ping", "Pong")

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
    generator = netconf_generator("./examples/forwarding/netconf.yml")
    objects, _ = next(generator)

    # Get the nodes and hosts.
    program_file_name = "./examples/forwarding/p4/forwarding.json"
    s1 = objects["components"]["s1"].p4device.load(program_file_name)
    s2 = objects["components"]["s2"].p4device.load(program_file_name)
    s3 = objects["components"]["s3"].p4device.load(program_file_name)
    s4 = objects["components"]["s4"].p4device.load(program_file_name)

    h1 = objects["components"]["h1"]

    # Populate the tables.
    s1.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.1.1')), 32),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:01:11')), 1],
    )
    s1.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.2.2')), 32),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:02:22')), 2],
    )
    s1.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.3.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:03:00')), 3],
    )
    s1.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.4.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:04:00')), 4],
    )

    s2.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.1.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:03:00')), 4],
    )
    s2.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.2.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:04:00')), 3],
    )
    s2.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.3.3')), 32),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:03:33')), 1],
    )
    s2.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.4.4')), 32),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:04:44')), 2],
    )

    s3.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.1.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:01:00')), 1],
    )
    s3.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.2.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:01:00')), 1],
    )
    s3.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.3.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:02:00')), 2],
    )
    s3.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.4.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:02:00')), 2],
    )

    s4.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.1.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:01:00')), 2],
    )
    s4.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.2.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:01:00')), 2],
    )
    s4.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.3.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:02:00')), 1],
    )
    s4.table("ingress", "MyIngress.ipv4_lpm").insert_entry(
        (int(ip_address('10.0.4.0')), 24),
        "MyIngress.ipv4_forward", [int(mac_address('08:00:00:00:02:00')), 1],
    )

    # Create a program here as well to make it easier to build packets.
    with open(program_file_name) as program_file:
        program = json.load(program_file)
    process = V1ModelProcess(__name__, program, packet_io=pyp4.PacketIO.STACK)

    # Build the ping packet.
    ipv4 = process.header("ipv4")
    ipv4["version"].val = 4
    ipv4["srcAddr"].val = int(ip_address('10.0.1.1'))
    ipv4["ttl"].val = int(255)

    ethernet = process.header("ethernet")
    ethernet["srcAddr"].val = int(mac_address('08:00:00:00:01:11'))
    ethernet["dstAddr"].val = int(mac_address('08:00:00:00:01:00'))
    ethernet["etherType"].val = 0x800

    ping = HeaderStack()
    ping.push(ipv4)
    ping.push(ethernet)
    ping.payload = "Ping: Hello, world!"

    # And send it!
    print(f"[{ns.sim_time():>6}] Host h1 sending ping to: 10.0.2.2 (TTL: {ipv4['ttl']})")
    ipv4["dstAddr"].val = int(ip_address('10.0.2.2'))
    h1.port.tx_output(deepcopy(ping))
    ns.sim_run(duration=1000)
    print()

    print(f"[{ns.sim_time():>6}] Host h1 sending ping to: 10.0.3.3 (TTL: {ipv4['ttl']})")
    ipv4["dstAddr"].val = int(ip_address('10.0.3.3'))
    h1.port.tx_output(deepcopy(ping))
    ns.sim_run(duration=1000)
    print()

    print(f"[{ns.sim_time():>6}] Host h1 sending ping to: 10.0.4.4 (TTL: {ipv4['ttl']})")
    ipv4["dstAddr"].val = int(ip_address('10.0.4.4'))
    h1.port.tx_output(deepcopy(ping))
    ns.sim_run(duration=1000)


if __name__ == "__main__":
    main()
