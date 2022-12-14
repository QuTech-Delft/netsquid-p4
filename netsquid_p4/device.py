"""Abstract base class for P4 devices."""

from abc import ABC, abstractmethod
import json
from typing import Dict, List, Optional

from netsquid.components.component import Component, Port
from netsquid.protocols import Protocol
from pyp4.packet import HeaderStack
from pyp4.processor import Process, Processor
from pyp4.table import Table

import netsquid as ns


class P4Device(ABC, Component):
    """Abstract base class for P4 devices. A P4 Device is a NetSquid component.

    Parameters
    ----------
    name
        The name for this device.
    p4_processor : pyp4.processor.Processor
        The P4 processor loaded with the P4 program.
    port_names : optional
        The names of the ports to add during construction.

    """

    P4_MAX_PORT = 0x1FF
    """Maximum allowed P4 port number."""

    def __init__(self, name: str, p4_processor: Processor, port_names: Optional[List[str]] = None):
        self.__port_protocols = {}
        Component.__init__(self, name, port_names=port_names)
        self.__p4_processor = p4_processor

    @property
    def _p4_processor(self) -> Processor:
        return self.__p4_processor

    def load(self, program_file_name: str) -> 'P4Device':
        """Load a P4 program onto the device processor.

        Parameters
        ----------
        program_file_name
            The file name with the P4 program in BM JSON format.

        Returns
        -------
        :
            For convenience the device itself is returned.

        """
        with open(program_file_name, encoding="utf-8") as program_file:
            program = json.load(program_file)
        process = self._create_process(program)
        self._p4_processor.load(process)
        return self

    def unload(self):
        """Unload the currently running P4 program."""
        self._p4_processor.unload()

    @abstractmethod
    def _create_process(self, program: Dict) -> Process:
        raise NotImplementedError

    def table(self, block: str, name: str) -> Table:
        """Access a table in the P4 processor.

        Parameters
        ----------
        block
            The name of the block in which the table is defined. Note that the name is defined by
            the architecture, not the program itself. E.g. the ingress block is called "ingress"
            regardless of how that block is called in the program.
        name
            The name of the table as defined by the program.

        Returns
        -------
        pyp4.table.Table
             The table.

        """
        try:
            return self.__p4_processor.table(block, name)
        except ValueError as verr:
            raise ValueError(f"Device {self.name} failed to access table :: {verr}") from verr

    def add_ports(self, names: List[str]) -> List[Port]:
        """Add ports to this component.

        Parameters
        ----------
        names
            List of the port names to add.

        Returns
        -------
        List[netsquid.components.component.Port]
            List of the ports with the given names.

        """
        for name in names:
            P4Device.validate_port_name(name)

        # Use superclass to formally add the ports.
        new_ports = super().add_ports(names)

        # Install the protocols on the new ports.
        for port in new_ports:
            self.__port_protocols[port.name] = PortProtocol(self, port).start()

        # Return the ports as that is what the superclass's add_ports does.
        return new_ports

    @staticmethod
    def validate_port_name(port_name: str) -> None:
        """Check whether the given port name is valid for a P4Device.

        Valid port names are positive integers that are less than or equal to `P4_MAX_PORT`.

        Parameters
        ----------
        port_name
            The port name to validate.

        Raises
        ------
        ValueError
             If the port name is not valid.

        """
        try:
            port_num = int(port_name, 0)
        except ValueError as error:
            raise ValueError(
                f"{port_name} is not an integer (P4Device ports must be integers)"
            ) from error
        if port_num > P4Device.P4_MAX_PORT:
            raise ValueError(
                f"{port_name} is greater than the maximum allowed value ({P4Device.P4_MAX_PORT})"
            )
        if port_name != str(int(port_name, 0)):
            raise ValueError(
                f"{port_name} != str(int({port_name}, 0)) [{str(int(port_name, 0))}]"
                "(P4Device port names must be reversibly convertible to strings)"
            )

    @abstractmethod
    def cnetwork_process(self, port_index: int, packet: HeaderStack) -> None:
        """Process an incoming classical network packet.

        Parameters
        ----------
        port_index
            The index of the port the packet arrived on.
        packet : pyp4.packet.HeaderStack
            The incoming packet.

        """
        raise NotImplementedError

    def _cnetwork_execute(self, port_index: int, packet: HeaderStack) -> None:
        """Send out a classical network packet generated by the P4 processor.

        Parameters
        ----------
        port_index
            The index of the egress port.
        packet : pyp4.packet.HeaderStack
            Outgoing packet.

        """
        self.ports[str(port_index)].tx_output(packet)


class PortProtocol(Protocol):
    """Listen for incoming packets, hand off to the P4 processor.

    Parameters
    ----------
    device
        The device on which this protocol is running.
    port : netsquid.components.component.Port
        The port to listen on.

    """

    def __init__(self, device: P4Device, port: Port):
        super().__init__(f"{device.name}-{port.name}")
        self.__device = device
        self.__port = port
        self.__port_index = int(port.name, 0)

    def run(self) -> None:
        """Run the protocol."""
        while True:
            yield self.await_port_input(self.__port)
            for packet_in in self.__port.rx_input().items:
                self.__device.cnetwork_process(self.__port_index, packet_in)


class NetsquidRuntime:
    """Base class for simulated runtimes in NetSquid.

    Parameters
    ----------
    magnitude : optional
        Time magnitude to use. Default is nanoseconds.
    """

    def __init__(self, magnitude: float = ns.NANOSECOND):
        super().__init__()
        self.__magnitude = magnitude
        self.__start_time = ns.sim_time(magnitude)

    def time(self) -> int:
        """Get the simulated time.

        Returns
        -------
        :
            The current time on the device. The clock must be set to 0 every time the switch starts.

        """
        return ns.sim_time(self.__magnitude) - self.__start_time
