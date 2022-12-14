"""A basic classical switch based on the v1model P4 architecture."""

from typing import Dict, List, Optional
import netsquid as ns
from pyp4.packet import HeaderStack
from pyp4.processor import Process
from pyp4.processors.v1model import (
    V1ModelProcessor,
    V1ModelRuntimeAbc,
    V1ModelProcess,
    V1ModelPortMeta,
)
import pyp4

from netsquid_p4.device import P4Device, NetsquidRuntime
from netsquid_p4.node import P4Node


class V1ModelNode(P4Node):
    """The V1Model architecture based node (NetSquid node).

    Parameters
    ----------
    name
        The name for this node.
    port_names : optional
        The names of the ports to add during construction.

    """

    def __init__(self, name: str, port_names: Optional[List[str]] = None):
        super().__init__(name, V1ModelDevice(f"{name}-v1model-device"), port_names=port_names)


class V1ModelDevice(P4Device):
    """The V1Model architecture based device (NetSquid component).

    Parameters
    ----------
    name
        The name for this device.
    port_names : optional
        The names of the ports to add during construction.

    """

    def __init__(self, name: str, port_names: Optional[List[str]] = None):
        runtime = V1ModelRuntime()
        p4_processor = V1ModelProcessor(runtime)
        super().__init__(name, p4_processor, port_names=port_names)

    def _create_process(self, program: Dict) -> Process:
        return V1ModelProcess(f"{self.name}-V1ModelProcess", program, pyp4.PacketIO.STACK)

    def cnetwork_process(self, port_index: int, packet: HeaderStack) -> None:
        """Process an incoming classical network packet.

        Parameters
        ----------
        port_index
            The index of the port the packet arrived on.
        packet : pyp4.packet.HeaderStack
            The incoming packet.

        """
        port_meta = V1ModelPortMeta(standard_metadata={"ingress_port": port_index})
        port_packets = self._p4_processor.input(port_meta, packet)
        for port_meta, packet_out in port_packets:
            self._cnetwork_execute(port_meta.standard_metadata["egress_port"], packet_out)


class V1ModelRuntime(V1ModelRuntimeAbc, NetsquidRuntime):
    """The simulation runtime for the V1Model switch."""

    def __init__(self):
        V1ModelRuntimeAbc.__init__(self)
        NetsquidRuntime.__init__(self, ns.MICROSECOND)

    def time(self) -> int:
        """Get the simulated time.

        Returns
        -------
        :
            The current time on the device in microseconds. The clock must be set to 0 every time
            the switch starts.

        """
        return NetsquidRuntime.time(self)
