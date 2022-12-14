"""Convenience base class for P4 nodes."""

from typing import List, Optional
from netsquid.components.component import Port
from netsquid.nodes.node import Node, QuantumMemory

from netsquid_p4.device import P4Device


class P4Node(Node):
    """Base class for P4 nodes. A P4Node is a NetSquid node with a P4Device as a subcomponent.

    A P4Node is largely just a NetSquid node with a P4Device subcomponent. However, whenever a port
    is added to the node, if it is a valid P4Device port name, a port with the same name will be
    added to the P4Device. Furthermore, the node port's input will be forwarded to that P4Device
    port, and the P4Device port's output will be forwarded to the node's port.

    The P4Node base class is provided for convenience as the simplest possible node that contains a
    P4Device. If the node's ports need to be connected the P4Device's ports differently then this
    base class should not be used.

    Parameters
    ----------
    name
        Name of node for display purposes.
    p4device
        The P4Device running a P4 processor.
    ID : optional
        Unique identifier for node e.g. its IP address.
    qmemory : netsquid.components.qmemory.QuantumMemory, optional
        The primary quantum memory component (or a derivative thereof) on this node.
    port_names : optional
        Names of additional ports to add to this component.

    """

    def __init__(
            self,
            name: str,
            p4device: P4Device,
            ID: int = None,
            qmemory: Optional[QuantumMemory] = None,
            port_names: Optional[List[str]] = None,
    ):
        # pylint: disable=too-many-arguments
        super().__init__(name, ID=ID, qmemory=qmemory)
        self.__p4device = p4device
        self.add_subcomponent(p4device)
        self.add_ports(port_names)

    @property
    def p4device(self) -> P4Device:
        """The P4Device subcomponent."""
        return self.__p4device

    def add_ports(self, names: List[str]) -> List[Port]:
        """Add ports to this component.

        For port names that are valid P4Device port names, a port with the same name will be added
        to the P4Device. Furthermore, the node port's input will be forwarded to that P4Device port,
        and the P4Device port's output will be forwarded to the node's port.

        Parameters
        ----------
        names
            Names of ports.

        Returns
        -------
        List[netsquid.components.component.Port]
            List of the ports with the given names.

        """
        new_ports = super().add_ports(names)

        p4device_port_names = []
        for port in new_ports:
            try:
                P4Device.validate_port_name(port.name)
                p4device_port_names.append(port.name)
            except ValueError:
                continue
        p4device_ports = self.__p4device.add_ports(p4device_port_names)

        for port in p4device_ports:
            self.ports[port.name].forward_input(port)
            port.forward_output(self.ports[port.name])

        return new_ports
