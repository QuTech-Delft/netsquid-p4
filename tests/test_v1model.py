"""Unit tests for the V1Model device."""

from copy import deepcopy
from functools import partial
import json
import pytest

from pyp4.packet import HeaderStack
from pyp4.processors.v1model import V1ModelProcess

from netsquid_p4.device import P4Device
from netsquid_p4.components.v1model import V1ModelDevice, V1ModelNode
from tests.util import assert_handler, handler


@pytest.fixture()
def program_file_name():
    return "tests/p4/v1model.json"


@pytest.fixture()
def process(program_file_name):
    with open(program_file_name) as program_file:
        program = json.load(program_file)
        return V1ModelProcess(__name__, program)


@pytest.fixture()
def device(program_file_name):
    return V1ModelDevice(name="v1model", port_names=["0"]).load(program_file_name)


@pytest.fixture()
def node(program_file_name):
    node = V1ModelNode(name="v1model", port_names=["0"])
    node.p4device.load(program_file_name)
    return node


def test_invalid_ports(process, node):
    invalid_port_names = [
        # Ports that exceed the maximum allowed value.
        str(P4Device.P4_MAX_PORT + 1),
        # Ports that are not integers.
        "port",
        # Ports that are not reversibly convertible back to a string.
        "0x10",
    ]

    for port_name in invalid_port_names:
        # Adding to the device directly should raise an error.
        with pytest.raises(ValueError):
            node.p4device.add_ports([port_name])

        # Adding to the node should not raise an error, but should not be added to the device.
        node.add_ports([port_name])
        assert port_name in node.ports
        assert port_name not in node.p4device.ports

        # Inject something into the node - nothing should happen.
        for port in node.ports.values():
            port.bind_output_handler(assert_handler)
        hdr = process.header("ping")
        hdr["ttl"].val = 100
        ping = HeaderStack()
        ping.push(hdr)
        node.ports[port_name].tx_input(ping)


def test_ping(ns, process, device):
    # Create ping packet.
    hdr = process.header("ping")
    hdr["ttl"].val = 100

    # Keep a copy of the header for verifications.
    verif = deepcopy(hdr)

    # We send the ping in 2 microsecond intervals.
    interval = 2_000

    # Run for 2 microseconds and ensure no packets are sent.
    device.ports["0"].bind_output_handler(assert_handler)
    ns.sim_run(duration=interval)

    # Prepare the store and handler.
    store = []
    device.ports["0"].bind_output_handler(partial(handler, store))

    # Run for 200_000 ns, i.e. a full 100xRTT.
    for ii in range(100):
        ping = HeaderStack()
        ping.push(hdr)
        device.ports["0"].tx_input(ping)
        ns.sim_run(duration=interval)

        if ii == 99:
            break

        assert len(store) == 1
        pong = store.pop()

        assert len(pong) == 1
        hdr = pong.pop()

        verif["ttl"].val -= 1
        assert "ttl" in hdr
        assert hdr["ttl"] == verif["ttl"]

        verif["ping_count"].val += 1
        assert "ping_count" in hdr
        assert hdr["ping_count"] == verif["ping_count"]

        verif["last_time"].val = verif["cur_time"].val
        assert "last_time" in hdr
        assert hdr["last_time"] == verif["last_time"]

        # We send the ping in 2 microsecond intervals.
        verif["cur_time"].val += (2_000 if device.name == "v1quantum" else 2)
        assert "cur_time" in hdr
        assert hdr["cur_time"] == verif["cur_time"]

    # We will have sent the last message with TTL 1 and not received a response
    assert not store
    assert verif["ttl"].val == 1

    # Run for another 200_000 ns to make sure that really nothing is coming back.
    device.ports["0"].bind_output_handler(assert_handler)
    ns.sim_run(duration=200_000)

    # Verify that unloading stops the processor.
    device.unload()
    hdr["ttl"].val = 100
    ping.push(hdr)
    device.ports["0"].tx_input(ping)
    with pytest.raises(RuntimeError):
        ns.sim_run(duration=interval)


def test_table(ns, process, device):
    # Create ping packet.
    hdr = process.header("ping")
    hdr["ttl"].val = 100

    # Try to access a table that does not exist.
    with pytest.raises(ValueError):
        assert device.table("ingress", "MyIngress.TableThatDoesNotExist") is not None

    # Insert an ingress rule to drop packets with TTL 100.
    device.table("ingress", "MyIngress.ping_ttl").insert_entry(100, "MyIngress.drop", [])

    # Run for 200_000 ns, i.e. a full 100xRTT and assert no message is sent back (since the ping is
    # dropped after matching the new entry).
    device.ports["0"].bind_output_handler(assert_handler)
    ping = HeaderStack()
    ping.push(hdr)
    device.ports["0"].tx_input(deepcopy(ping))
    ns.sim_run(duration=200_000)
